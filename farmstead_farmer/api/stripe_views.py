import json
import importlib
import calendar
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, throttle_classes

from api.throttles import MainAPiThrottle
from api.models import CustomUser
from core.infrastructure.repositories import DjangoUserRepository

try:
    import stripe
except Exception:  # pragma: no cover
    stripe = None


user_repository = DjangoUserRepository()


def _json_error(message: str, status: int = 400):
    return JsonResponse({'error': message}, status=status)


def _get_token_from_request(request):
    token = None
    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')
            token = data.get('token')
        except json.JSONDecodeError:
            return None

    if token:
        return token

    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Token '):
        return auth_header.replace('Token ', '', 1).strip()
    if auth_header.startswith('Bearer '):
        return auth_header.replace('Bearer ', '', 1).strip()

    return None


def _get_user_by_token(request):
    token = _get_token_from_request(request)
    if not token:
        return None
    return user_repository.find_by_token(token)


def _configure_stripe():
    global stripe
    if stripe is None:
        try:
            stripe = importlib.import_module('stripe')
        except Exception:
            stripe = None

    if stripe is None:
        return False
    secret = getattr(settings, 'STRIPE_SECRET_KEY', '')
    if not secret:
        return False
    stripe.api_key = secret
    return True


def _stripe_list_data(value):
    if value is None:
        return []
    if isinstance(value, dict):
        data = value.get('data', [])
        return data if isinstance(data, list) else []
    data_attr = getattr(value, 'data', None)
    if isinstance(data_attr, list):
        return data_attr
    return []


def _subscription_period_end(subscription_obj):
    if not subscription_obj:
        return None

    top_level = subscription_obj.get('current_period_end')
    if top_level:
        return int(top_level)

    items = subscription_obj.get('items', {})
    item_data = []
    if isinstance(items, dict):
        item_data = items.get('data', []) or []
    else:
        data_attr = getattr(items, 'data', None)
        if isinstance(data_attr, list):
            item_data = data_attr

    if item_data:
        item_end = item_data[0].get('current_period_end')
        if item_end:
            return int(item_end)

    trial_end = subscription_obj.get('trial_end')
    if trial_end:
        return int(trial_end)

    return None


def _normalize_plan(plan_value):
    plan = str(plan_value or '').strip().lower()
    return plan if plan in ('monthly', 'annual') else None


def _plan_from_subscription(subscription_obj):
    if not subscription_obj:
        return None

    items = subscription_obj.get('items', {})
    item_data = []
    if isinstance(items, dict):
        item_data = items.get('data', []) or []
    else:
        data_attr = getattr(items, 'data', None)
        if isinstance(data_attr, list):
            item_data = data_attr

    monthly_price = str(getattr(settings, 'STRIPE_MONTHLY_PRICE_ID', '') or '').strip()
    annual_price = str(getattr(settings, 'STRIPE_ANNUAL_PRICE_ID', '') or '').strip()

    for item in item_data:
        price = item.get('price')
        price_id = ''
        recurring_interval = ''

        if isinstance(price, dict):
            price_id = str(price.get('id') or '').strip()
            recurring = price.get('recurring') or {}
            if isinstance(recurring, dict):
                recurring_interval = str(recurring.get('interval') or '').strip().lower()
        elif isinstance(price, str):
            price_id = price.strip()
        else:
            price_id = str(getattr(price, 'id', '') or '').strip()
            recurring = getattr(price, 'recurring', None)
            if isinstance(recurring, dict):
                recurring_interval = str(recurring.get('interval') or '').strip().lower()

        # Older Stripe payloads may use nested `plan.interval` on subscription items.
        plan_data = item.get('plan') or {}
        if isinstance(plan_data, dict):
            recurring_interval = recurring_interval or str(plan_data.get('interval') or '').strip().lower()

        if not price_id:
            if recurring_interval == 'month':
                return 'monthly'
            if recurring_interval == 'year':
                return 'annual'
            continue

        if monthly_price and price_id == monthly_price:
            return 'monthly'
        if annual_price and price_id == annual_price:
            return 'annual'

        if recurring_interval == 'month':
            return 'monthly'
        if recurring_interval == 'year':
            return 'annual'

    return None


def _plan_from_checkout_session(checkout_session):
    if not checkout_session:
        return None

    monthly_price = str(getattr(settings, 'STRIPE_MONTHLY_PRICE_ID', '') or '').strip()
    annual_price = str(getattr(settings, 'STRIPE_ANNUAL_PRICE_ID', '') or '').strip()

    session_id = str(checkout_session.get('id') or '').strip()
    if not session_id:
        return None

    line_items = []
    inline_line_items = checkout_session.get('line_items')
    if isinstance(inline_line_items, dict):
        line_items = inline_line_items.get('data', []) or []

    if not line_items:
        try:
            listed = stripe.checkout.Session.list_line_items(session_id, limit=10)
            line_items = _stripe_list_data(listed)
        except Exception:
            line_items = []

    for item in line_items:
        price = item.get('price')
        price_id = ''
        if isinstance(price, dict):
            price_id = str(price.get('id') or '').strip()
        elif isinstance(price, str):
            price_id = price.strip()
        else:
            price_id = str(getattr(price, 'id', '') or '').strip()

        if monthly_price and price_id == monthly_price:
            return 'monthly'
        if annual_price and price_id == annual_price:
            return 'annual'

    return None


def _add_months(dt_value, months):
    month_index = dt_value.month - 1 + months
    year = dt_value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(dt_value.day, calendar.monthrange(year, month)[1])
    return dt_value.replace(year=year, month=month, day=day)


def _extend_user_subscription(user, plan):
    plan = _normalize_plan(plan)
    if not plan:
        return False

    now = datetime.now(dt_timezone.utc)
    current_expiry = user.subscription_expires_at
    base = current_expiry if current_expiry and current_expiry > now else now

    if plan == 'monthly':
        new_expiry = _add_months(base, 1)
    else:
        new_expiry = _add_months(base, 12)

    user.subscription_expires_at = new_expiry
    user.save(update_fields=['subscription_expires_at'])
    return True


def _apply_stacked_extension(user, plan, session_id=None):
    plan = _normalize_plan(plan)
    if not plan:
        return False

    if session_id:
        cache_key = f'stripe_checkout_extended:{session_id}'
        if cache.get(cache_key):
            return False

    applied = _extend_user_subscription(user, plan)
    if applied and session_id:
        cache.set(cache_key, True, timeout=60 * 60 * 24 * 45)
    return applied


def _sync_from_checkout_session(user, session_id):
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    subscription_id = checkout_session.get('subscription')
    if not subscription_id:
        raise ValueError('Сесія не містить підписки.')

    session_user_id = str(checkout_session.get('client_reference_id') or '')
    session_email = str(checkout_session.get('customer_email') or '')
    if session_user_id and session_user_id != str(user.id):
        raise PermissionError('Сесія не належить цьому користувачу.')
    if session_email and user.email and session_email.lower() != user.email.lower():
        raise PermissionError('Сесія не належить цьому користувачу.')

    session_plan = _normalize_plan(checkout_session.get('metadata', {}).get('plan'))
    if not session_plan:
        subscription = stripe.Subscription.retrieve(subscription_id)
        session_plan = _normalize_plan(subscription.get('metadata', {}).get('plan')) or _plan_from_subscription(subscription)
    if not session_plan:
        session_plan = _plan_from_checkout_session(checkout_session)

    if session_plan:
        _apply_stacked_extension(user, session_plan, session_id=session_id)
        return

    subscription = stripe.Subscription.retrieve(subscription_id)
    period_end_ts = _subscription_period_end(subscription)
    if not period_end_ts:
        raise ValueError('Не вдалося визначити дату завершення передплати.')

    period_end_dt = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)
    if not user.subscription_expires_at or period_end_dt > user.subscription_expires_at:
        user.subscription_expires_at = period_end_dt
        user.save(update_fields=['subscription_expires_at'])


@api_view(['POST'])
@throttle_classes([MainAPiThrottle])
def subscription_status(request):
    user = _get_user_by_token(request)
    if user is None:
        return _json_error('Невірний або відсутній токен.', 401)

    if _configure_stripe() and (not user.subscription_expires_at or not user.has_active_subscription):
        try:
            customers = stripe.Customer.list(email=user.email, limit=1)
            customer_data = _stripe_list_data(customers)
            customer_id = customer_data[0].get('id') if customer_data else None
            if customer_id:
                subscriptions = stripe.Subscription.list(customer=customer_id, status='all', limit=20)
                subs_data = _stripe_list_data(subscriptions)
                best_end = None
                for sub in subs_data:
                    period_end = _subscription_period_end(sub)
                    if period_end and (best_end is None or int(period_end) > int(best_end)):
                        best_end = int(period_end)
                if best_end:
                    user.subscription_expires_at = datetime.fromtimestamp(best_end, tz=dt_timezone.utc)
                    user.save(update_fields=['subscription_expires_at'])
        except Exception:
            pass

    expires_at = user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
    return JsonResponse({
        'has_active_subscription': user.has_active_subscription,
        'subscription_expires_at': expires_at,
    })


@api_view(['POST'])
@throttle_classes([MainAPiThrottle])
def create_checkout_session(request):
    if not _configure_stripe():
        return _json_error('Stripe не налаштовано на сервері.', 500)

    user = _get_user_by_token(request)
    if user is None:
        return _json_error('Невірний або відсутній токен.', 401)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return _json_error('Некоректний JSON.')

    plan = data.get('plan')
    if plan not in ('monthly', 'annual'):
        return _json_error('Невірний тариф. Дозволено: monthly, annual.')

    price_id = settings.STRIPE_MONTHLY_PRICE_ID if plan == 'monthly' else settings.STRIPE_ANNUAL_PRICE_ID
    if not price_id:
        return _json_error('Stripe price_id не налаштовано.', 500)

    success_url = request.build_absolute_uri('/map/subscription/')
    cancel_url = request.build_absolute_uri('/map/subscription/')

    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            billing_address_collection='auto',
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(user.id),
            metadata={
                'user_id': str(user.id),
                'plan': plan,
            },
            subscription_data={
                'metadata': {
                    'user_id': str(user.id),
                    'plan': plan,
                },
            },
            customer_email=user.email,
            allow_promotion_codes=True,
        )
        cache.set(f'stripe_last_checkout_session:{user.id}', str(session.id), timeout=60 * 60 * 6)
    except Exception as error:
        return _json_error(f'Stripe checkout error: {error}', 500)

    return JsonResponse({'url': session.url})


@api_view(['POST'])
@throttle_classes([MainAPiThrottle])
def sync_subscription(request):
    if not _configure_stripe():
        return _json_error('Stripe не налаштовано на сервері.', 500)

    user = _get_user_by_token(request)
    if user is None:
        return _json_error('Невірний або відсутній токен.', 401)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return _json_error('Некоректний JSON.')

    session_id = str(data.get('session_id') or '').strip()
    if not session_id:
        session_id = str(cache.get(f'stripe_last_checkout_session:{user.id}') or '').strip()

    if session_id:
        try:
            _sync_from_checkout_session(user, session_id)
            return JsonResponse({
                'status': 'ok',
                'has_active_subscription': user.has_active_subscription,
                'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            })
        except PermissionError as error:
            return _json_error(str(error), 403)
        except ValueError as error:
            return _json_error(str(error), 400)
        except Exception as error:
            return _json_error(f'Subscription sync error: {error}', 500)

    try:
        customers = stripe.Customer.list(email=user.email, limit=1)
        customer_data = _stripe_list_data(customers)
        customer_id = customer_data[0].get('id') if customer_data else None

        if not customer_id:
            expires_at = user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
            return JsonResponse({
                'status': 'ok',
                'has_active_subscription': user.has_active_subscription,
                'subscription_expires_at': expires_at,
            })

        subscriptions = stripe.Subscription.list(customer=customer_id, status='all', limit=20)
        subs_data = _stripe_list_data(subscriptions)

        best_end = None
        for sub in subs_data:
            period_end = _subscription_period_end(sub)
            if period_end and (best_end is None or int(period_end) > int(best_end)):
                best_end = int(period_end)

        if best_end:
            best_end_dt = datetime.fromtimestamp(best_end, tz=dt_timezone.utc)
            if not user.subscription_expires_at or best_end_dt > user.subscription_expires_at:
                user.subscription_expires_at = best_end_dt
                user.save(update_fields=['subscription_expires_at'])

        return JsonResponse({
            'status': 'ok',
            'has_active_subscription': user.has_active_subscription,
            'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
        })
    except Exception as error:
        return _json_error(f'Subscription lookup error: {error}', 500)

    return JsonResponse({
        'status': 'ok',
        'has_active_subscription': user.has_active_subscription,
        'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
    })


@csrf_exempt
def stripe_webhook(request):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    if not _configure_stripe():
        return _json_error('Stripe не налаштовано на сервері.', 500)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = json.loads(payload.decode('utf-8'))
    except Exception as error:
        return _json_error(f'Webhook signature error: {error}', 400)

    event_type = event.get('type')
    data_object = event.get('data', {}).get('object', {})

    def resolve_user(user_id=None, customer_id=None):
        user = CustomUser.objects.filter(id=int(user_id)).first() if str(user_id).isdigit() else None
        if user is not None:
            return user
        if customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                email = str(customer.get('email') or '').strip().lower()
                if email:
                    return CustomUser.objects.filter(email__iexact=email).first()
            except Exception:
                return None
        return None

    def update_subscription_expiry(user_id, period_end_ts, customer_id=None):
        user = resolve_user(user_id=user_id, customer_id=customer_id)
        if user is None:
            return

        if period_end_ts:
            period_end_dt = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)
            if user.subscription_expires_at and user.subscription_expires_at > period_end_dt:
                return
            user.subscription_expires_at = period_end_dt
        else:
            user.subscription_expires_at = None
        user.save(update_fields=['subscription_expires_at'])

    try:
        if event_type == 'checkout.session.completed':
            user_id = data_object.get('metadata', {}).get('user_id') or data_object.get('client_reference_id')
            subscription_id = data_object.get('subscription')
            customer_id = data_object.get('customer')
            session_id = data_object.get('id')
            user = resolve_user(user_id=user_id, customer_id=customer_id)
            if user is not None:
                subscription = None
                session_plan = _normalize_plan(data_object.get('metadata', {}).get('plan'))
                if not session_plan and subscription_id:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    session_plan = _normalize_plan(subscription.get('metadata', {}).get('plan')) or _plan_from_subscription(subscription)
                if not session_plan:
                    session_plan = _plan_from_checkout_session(data_object)
                if session_plan:
                    _apply_stacked_extension(user, session_plan, session_id=session_id)
                elif subscription_id:
                    if subscription is None:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                    update_subscription_expiry(user_id, _subscription_period_end(subscription), customer_id=customer_id)

        elif event_type in ('customer.subscription.updated', 'customer.subscription.created'):
            user_id = data_object.get('metadata', {}).get('user_id')
            customer_id = data_object.get('customer')
            update_subscription_expiry(user_id, _subscription_period_end(data_object), customer_id=customer_id)

        elif event_type in ('customer.subscription.deleted',):
            user_id = data_object.get('metadata', {}).get('user_id')
            customer_id = data_object.get('customer')
            update_subscription_expiry(user_id, None, customer_id=customer_id)

    except Exception as error:
        return _json_error(f'Webhook processing error: {error}', 500)

    return JsonResponse({'status': 'ok'})
