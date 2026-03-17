import { fetchJson } from "../core/http.js";
import { Card } from "../components/Card.js";

const e = React.createElement;

export function AnimalsPage() {
    const _a = React.useState([]), animals = _a[0], setAnimals = _a[1];

    React.useEffect(function () {
        fetchJson("/api/animals/")
            .then(function (data) { setAnimals(data || []); })
            .catch(function () { setAnimals([]); });
    }, []);

    return e(
        "section",
        { className: "page" },
        e("h1", null, "Animals"),
        e(
            "div",
            { className: "grid" },
            animals.map(function (animal) {
                return e(Card, {
                    key: animal.id,
                    image: animal.image,
                    title: animal.name,
                    link: "/catalog/animals/" + animal.id + "/",
                });
            }),
        ),
    );
}
