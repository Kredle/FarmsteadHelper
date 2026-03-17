import { fetchJson } from "../core/http.js";
import { Link } from "../components/Link.js";

const e = React.createElement;

export function ForumPage() {
    const _a = React.useState([]), topics = _a[0], setTopics = _a[1];

    React.useEffect(function () {
        fetchJson("/forum/get_topics")
            .then(function (data) { setTopics(data || []); })
            .catch(function () { setTopics([]); });
    }, []);

    return e(
        "section",
        { className: "page" },
        e("h1", null, "Forum"),
        e(
            "div",
            { className: "list" },
            topics.map(function (topic) {
                return e(
                    "article",
                    { key: topic.idTopic, className: "list-item" },
                    e(Link, { to: "/forum/topic/" + topic.idTopic + "/", className: "topic-link" }, topic.Title),
                    e("p", null, topic.Content),
                    e("small", null, (topic.Author || "Unknown") + " | likes: " + (topic.Likes || 0)),
                );
            }),
        ),
    );
}
