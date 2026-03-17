import { fetchJson } from "../core/http.js";
import { Card } from "../components/Card.js";

const e = React.createElement;

export function CatalogPage() {
    const _a = React.useState([]), items = _a[0], setItems = _a[1];
    const _b = React.useState("all"), filter = _b[0], setFilter = _b[1];

    React.useEffect(function () {
        fetchJson("/api/catalog-items/")
            .then(function (data) { setItems(data.items || []); })
            .catch(function () { setItems([]); });
    }, []);

    const visible = items.filter(function (item) {
        return filter === "all" ? true : item.category === filter;
    });

    return e(
        "section",
        { className: "page" },
        e("h1", null, "Catalog"),
        e(
            "div",
            { className: "filters" },
            ["all", "animals", "flowers", "vegetables", "trees"].map(function (value) {
                return e(
                    "button",
                    {
                        key: value,
                        className: filter === value ? "btn active" : "btn",
                        onClick: function () { setFilter(value); },
                    },
                    value,
                );
            }),
        ),
        e(
            "div",
            { className: "grid" },
            visible.map(function (item, index) {
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
