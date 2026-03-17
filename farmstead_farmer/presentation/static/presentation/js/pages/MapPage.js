import { fetchJson } from "../core/http.js";

const e = React.createElement;

export function MapPage(props) {
    const _a = React.useState(props.userId || ""), userId = _a[0], setUserId = _a[1];
    const _b = React.useState(null), mapInfo = _b[0], setMapInfo = _b[1];
    const _c = React.useState(""), error = _c[0], setError = _c[1];

    function loadMap(targetUserId) {
        if (!targetUserId) {
            setError("Enter user id");
            setMapInfo(null);
            return;
        }
        setError("");
        fetchJson("/map/get-map/" + targetUserId + "/")
            .then(function (data) { setMapInfo(data || null); })
            .catch(function (err) {
                setMapInfo(null);
                setError(err.message || "Could not load map");
            });
    }

    React.useEffect(function () {
        if (props.userId) {
            loadMap(props.userId);
        }
    }, [props.userId]);

    return e(
        "section",
        { className: "page" },
        e("h1", null, "Interactive Map"),
        e("p", { className: "lead" }, "Map data is loaded through the API and rendered by the SPA."),
        e(
            "form",
            {
                className: "form",
                onSubmit: function (event) {
                    event.preventDefault();
                    loadMap(userId);
                },
            },
            e("input", {
                value: userId,
                onChange: function (ev) { setUserId(ev.target.value); },
                placeholder: "Owner user id",
                required: true,
            }),
            e("button", { type: "submit", className: "btn active" }, "Load map"),
        ),
        error ? e("p", { className: "error" }, error) : null,
        mapInfo
            ? e(
                  "div",
                  { className: "list" },
                  e(
                      "article",
                      { className: "list-item" },
                      e("p", null, "Owner: " + mapInfo.owner_id),
                      e("p", null, mapInfo.exists ? "Map found" : "No map for this user"),
                      mapInfo.exists
                          ? e("pre", null, typeof mapInfo.map_data === "string" ? mapInfo.map_data : JSON.stringify(mapInfo.map_data, null, 2))
                          : null,
                  ),
              )
            : null,
    );
}
