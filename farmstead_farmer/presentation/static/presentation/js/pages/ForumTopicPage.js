import { fetchJson } from "../core/http.js";

const e = React.createElement;

export function ForumTopicPage(props) {
    const _a = React.useState(null), topic = _a[0], setTopic = _a[1];
    const _b = React.useState([]), comments = _b[0], setComments = _b[1];

    React.useEffect(function () {
        fetchJson("/forum/api/topic/" + props.topicId + "/")
            .then(function (data) { setTopic(data); })
            .catch(function () { setTopic(null); });

        fetchJson("/forum/topic/" + props.topicId + "/comments_list/")
            .then(function (data) { setComments(data || []); })
            .catch(function () { setComments([]); });
    }, [props.topicId]);

    if (!topic) {
        return e("section", { className: "page" }, e("p", null, "Loading..."));
    }

    return e(
        "section",
        { className: "page" },
        e("h1", null, topic.title),
        e("p", { className: "lead" }, topic.content),
        e("p", null, "Category: " + (topic.category || "-")),
        e("p", null, "Author: " + (topic.author || "-")),
        e("h2", null, "Comments"),
        e(
            "div",
            { className: "list" },
            comments.map(function (comment) {
                return e(
                    "article",
                    { key: comment.idComments, className: "list-item" },
                    e("p", null, comment.Content),
                    e("small", null, (comment.Author || "Unknown") + " | likes: " + (comment.Likes || 0)),
                );
            }),
        ),
    );
}
