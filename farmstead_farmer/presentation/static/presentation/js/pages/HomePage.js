import { fetchJson } from "../core/http.js";
import { Card } from "../components/Card.js";

const e = React.createElement;

export function HomePage() {
    const _a = React.useState([]), items = _a[0], setItems = _a[1];
    const _b = React.useState(true), loading = _b[0], setLoading = _b[1];

    React.useEffect(function () {
        fetchJson("/api/catalog-items/")
            .then(function (data) { setItems(data.items || []); })
            .catch(function () { setItems([]); })
            .finally(function () { setLoading(false); });
    }, []);

    return e(
        "section",
        { className: "page" },
        e("h1", null, "FarmsteadHelper"),
        e("p", { className: "lead" }, "React presentation layer is now serving the main user routes."),
        loading
            ? e("p", null, "Loading...")
            : e(
                  "div",
                  { className: "grid" },
                  items.map(function (item, index) {
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
