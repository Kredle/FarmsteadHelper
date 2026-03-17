import { fetchJson } from "../core/http.js";

const e = React.createElement;

export function AnimalDetailPage(props) {
    const _a = React.useState(null), item = _a[0], setItem = _a[1];
    const _b = React.useState(false), favorite = _b[0], setFavorite = _b[1];
    const token = localStorage.getItem("authToken");

    React.useEffect(function () {
        fetchJson("/api/animals/" + props.animalId + "/" + props.sortId + "/")
            .then(function (data) { setItem(data || null); })
            .catch(function () { setItem(null); });
    }, [props.animalId, props.sortId]);

    React.useEffect(function () {
        if (!item || !token) {
            return;
        }
        const payload = {
            token: token,
            name: item.common_name,
            image_url: item.image,
            link: window.location.href,
            category: "Тварини",
        };
        fetchJson("/api/check_favorite/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (data) { setFavorite(data.status === "inside"); })
            .catch(function () { setFavorite(false); });
    }, [item, token]);

    function toggleFavorite() {
        if (!item || !token) {
            return;
        }
        const payload = {
            token: token,
            name: item.common_name,
            image_url: item.image,
            link: window.location.href,
            category: "Тварини",
        };
        fetchJson("/api/toggle_favorite/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (data) { setFavorite(data.status === "added"); })
            .catch(function () { setFavorite(false); });
    }

    if (!item) {
        return e("section", { className: "page" }, e("p", null, "Loading..."));
    }

    return e(
        "section",
        { className: "page" },
        e("h1", null, item.common_name || "Animal detail"),
        item.image ? e("img", { className: "hero-image", src: item.image, alt: item.common_name || "animal" }) : null,
        e("p", { className: "lead" }, item.description || "No description."),
        token
            ? e(
                  "button",
                  { className: favorite ? "btn active" : "btn", onClick: toggleFavorite },
                  favorite ? "Remove from favorites" : "Add to favorites",
              )
            : null,
        e(
            "dl",
            { className: "details" },
            e("dt", null, "Scientific name"), e("dd", null, item.scientific_name || "-"),
            e("dt", null, "Class"), e("dd", null, item.class_field || "-"),
            e("dt", null, "Family"), e("dd", null, item.family || "-"),
            e("dt", null, "Habitat"), e("dd", null, item.habitat || "-"),
        ),
    );
}
