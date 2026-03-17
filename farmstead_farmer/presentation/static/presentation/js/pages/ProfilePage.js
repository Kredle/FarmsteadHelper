import { fetchJson } from "../core/http.js";
import { Card } from "../components/Card.js";

const e = React.createElement;

export function ProfilePage(props) {
    const _a = React.useState([]), favorites = _a[0], setFavorites = _a[1];
    const _b = React.useState(""), error = _b[0], setError = _b[1];
    const token = localStorage.getItem("authToken");

    React.useEffect(function () {
        if (!token) {
            setError("Please sign in to view profile details.");
            return;
        }
        fetchJson("/api/check_profile/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: token, username: props.username }),
        })
            .then(function (data) { setFavorites(data.favorites || []); })
            .catch(function (err) { setError(err.message || "Could not load profile."); });
    }, [props.username, token]);

    return e(
        "section",
        { className: "page" },
        e("h1", null, "Profile: " + props.username),
        error ? e("p", { className: "error" }, error) : null,
        e(
            "div",
            { className: "grid" },
            favorites.map(function (item, index) {
                return e(Card, {
                    key: String(index) + "-" + (item.url || ""),
                    image: item.image_url,
                    title: item.common_name,
                    subtitle: item.category,
                    link: item.url,
                });
            }),
        ),
    );
}
