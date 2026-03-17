import { fetchJson } from "../core/http.js";
import { Link } from "../components/Link.js";
import { navigate } from "../core/navigation.js";

const e = React.createElement;

export function AuthPage(props) {
    const _a = React.useState(""), username = _a[0], setUsername = _a[1];
    const _b = React.useState(""), password = _b[0], setPassword = _b[1];
    const _c = React.useState(""), email = _c[0], setEmail = _c[1];
    const _d = React.useState(""), firstname = _d[0], setFirstname = _d[1];
    const _e = React.useState(""), lastname = _e[0], setLastname = _e[1];
    const _f = React.useState(""), message = _f[0], setMessage = _f[1];

    function submit(event) {
        event.preventDefault();
        if (props.mode === "login") {
            fetchJson("/api/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username, password: password }),
            })
                .then(function (data) {
                    if (data.token) {
                        localStorage.setItem("authToken", data.token);
                        navigate("/");
                        return;
                    }
                    setMessage("No token returned.");
                })
                .catch(function (err) { setMessage(err.message); });
            return;
        }

        fetchJson("/api/register/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                email: email,
                firstname: firstname,
                lastname: lastname,
                password: password,
                repeat_password: password,
            }),
        })
            .then(function () { setMessage("Registration successful. You can now sign in."); })
            .catch(function (err) { setMessage(err.message); });
    }

    if (props.mode !== "login" && props.mode !== "register") {
        return e(
            "section",
            { className: "page" },
            e("h1", null, "This route is now handled by React"),
            e("p", { className: "lead" }, "The legacy Django template was replaced by the SPA shell."),
            e(Link, { to: "/" }, "Go home"),
        );
    }

    return e(
        "section",
        { className: "page" },
        e("h1", null, props.mode === "login" ? "Sign in" : "Create account"),
        e(
            "form",
            { className: "form", onSubmit: submit },
            e("input", { value: username, onChange: function (ev) { setUsername(ev.target.value); }, placeholder: "Username", required: true }),
            props.mode === "register" ? e("input", { value: email, onChange: function (ev) { setEmail(ev.target.value); }, placeholder: "Email", required: true, type: "email" }) : null,
            props.mode === "register" ? e("input", { value: firstname, onChange: function (ev) { setFirstname(ev.target.value); }, placeholder: "First name", required: true }) : null,
            props.mode === "register" ? e("input", { value: lastname, onChange: function (ev) { setLastname(ev.target.value); }, placeholder: "Last name", required: true }) : null,
            e("input", { value: password, onChange: function (ev) { setPassword(ev.target.value); }, placeholder: "Password", required: true, type: "password" }),
            e("button", { type: "submit", className: "btn active" }, props.mode === "login" ? "Sign in" : "Register"),
        ),
        message ? e("p", { className: "lead" }, message) : null,
    );
}
