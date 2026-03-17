import { fetchJson } from "../core/http.js";
import { Card } from "../components/Card.js";

const e = React.createElement;

export function AnimalSortsPage(props) {
    const _a = React.useState([]), sorts = _a[0], setSorts = _a[1];
    const _b = React.useState(""), animalName = _b[0], setAnimalName = _b[1];

    React.useEffect(function () {
        fetchJson("/api/animals/" + props.animalId + "/")
            .then(function (data) {
                setAnimalName(data.animal && data.animal.name ? data.animal.name : "Animal");
                setSorts(data.sorts || []);
            })
            .catch(function () { setSorts([]); });
    }, [props.animalId]);

    return e(
        "section",
        { className: "page" },
        e("h1", null, animalName),
        e(
            "div",
            { className: "grid" },
            sorts.map(function (sort) {
                return e(Card, {
                    key: sort.id,
                    image: sort.image,
                    title: sort.name,
                    link: "/catalog/animals/" + props.animalId + "/" + sort.id + "/",
                });
            }),
        ),
    );
}
