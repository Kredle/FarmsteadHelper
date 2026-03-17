import { fetchJson } from "./core/http.js";
import { TopNav } from "./components/TopNav.js";
import { HomePage } from "./pages/HomePage.js";
import { CatalogPage } from "./pages/CatalogPage.js";
import { AnimalsPage } from "./pages/AnimalsPage.js";
import { AnimalSortsPage } from "./pages/AnimalSortsPage.js";
import { AnimalDetailPage } from "./pages/AnimalDetailPage.js";
import { ForumPage } from "./pages/ForumPage.js";
import { ForumTopicPage } from "./pages/ForumTopicPage.js";
import { MapPage } from "./pages/MapPage.js";
import { ProfilePage } from "./pages/ProfilePage.js";
import { AuthPage } from "./pages/AuthPage.js";
import { NotFoundPage } from "./pages/NotFoundPage.js";

const e = React.createElement;

function matchRoute(pathname) {
    let m;
    if (pathname === "/") return { name: "home" };
    if (pathname === "/catalog" || pathname === "/catalog/") return { name: "catalog" };
    if (pathname === "/catalog/animals" || pathname === "/catalog/animals/") return { name: "animals" };
    m = pathname.match(/^\/catalog\/animals\/(\d+)\/?$/);
    if (m) return { name: "animal-sorts", animalId: m[1] };
    m = pathname.match(/^\/catalog\/animals\/(\d+)\/(\d+)\/?$/);
    if (m) return { name: "animal-detail", animalId: m[1], sortId: m[2] };
    if (pathname === "/forum" || pathname === "/forum/") return { name: "forum" };
    m = pathname.match(/^\/forum\/topic\/(\d+)\/?$/);
    if (m) return { name: "forum-topic", topicId: m[1] };
    if (pathname === "/map" || pathname === "/map/") return { name: "map" };
    if (pathname === "/map/interactive-map" || pathname === "/map/interactive-map/") return { name: "map" };
    m = pathname.match(/^\/map\/get-map\/(\d+)\/?$/);
    if (m) return { name: "map", userId: m[1] };
    m = pathname.match(/^\/profile\/([^/]+)\/?$/);
    if (m) return { name: "profile", username: decodeURIComponent(m[1]) };
    if (pathname === "/login" || pathname === "/login/") return { name: "auth", mode: "login" };
    if (pathname === "/register" || pathname === "/register/") return { name: "auth", mode: "register" };
    if (pathname === "/reset-password" || pathname === "/reset-password/") return { name: "auth", mode: "reset" };
    if (pathname === "/new-password" || pathname === "/new-password/") return { name: "auth", mode: "new" };
    if (pathname === "/confirm-register" || pathname === "/confirm-register/") return { name: "auth", mode: "confirm" };
    if (pathname === "/edit-profile" || pathname === "/edit-profile/") return { name: "auth", mode: "edit-profile" };
    return { name: "404" };
}

function App() {
    const _a = React.useState(window.location.pathname), pathname = _a[0], setPathname = _a[1];
    const _b = React.useState(null), user = _b[0], setUser = _b[1];

    React.useEffect(function () {
        function onPopState() {
            setPathname(window.location.pathname);
        }
        window.addEventListener("popstate", onPopState);
        return function () {
            window.removeEventListener("popstate", onPopState);
        };
    }, []);

    React.useEffect(function () {
        const token = localStorage.getItem("authToken");
        if (!token) {
            setUser(null);
            return;
        }
        fetchJson("/api/user-data/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: token }),
        })
            .then(function (data) { setUser(data || null); })
            .catch(function () { setUser(null); });
    }, [pathname]);

    const route = matchRoute(pathname);
    let page = null;

    if (route.name === "home") page = e(HomePage);
    else if (route.name === "catalog") page = e(CatalogPage);
    else if (route.name === "animals") page = e(AnimalsPage);
    else if (route.name === "animal-sorts") page = e(AnimalSortsPage, { animalId: route.animalId });
    else if (route.name === "animal-detail") page = e(AnimalDetailPage, { animalId: route.animalId, sortId: route.sortId });
    else if (route.name === "forum") page = e(ForumPage);
    else if (route.name === "forum-topic") page = e(ForumTopicPage, { topicId: route.topicId });
    else if (route.name === "map") page = e(MapPage, { userId: route.userId });
    else if (route.name === "profile") page = e(ProfilePage, { username: route.username });
    else if (route.name === "auth") page = e(AuthPage, { mode: route.mode });
    else page = e(NotFoundPage);

    return e(
        "main",
        { className: "app-shell" },
        e(TopNav, { user: user }),
        page,
    );
}

const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement);
root.render(e(App));
