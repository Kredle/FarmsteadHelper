export function fetchJson(url, options) {
    return fetch(url, options).then(function (response) {
        if (!response.ok) {
            return response
                .json()
                .catch(function () {
                    return {};
                })
                .then(function (payload) {
                    const message = payload.detail || payload.error || payload.message || "Request failed";
                    throw new Error(message);
                });
        }
        return response.json().catch(function () {
            return {};
        });
    });
}
