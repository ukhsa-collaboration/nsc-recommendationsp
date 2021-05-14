import Cookie from "js-cookie";

const USE_TRACKING_DISABLED_COOKIE_NAME = "useTrackingDisabled";

const disableUseTracking = () => {
    Cookie.remove("_ga");
    Cookie.remove("_gid");
    return Cookie.set(USE_TRACKING_DISABLED_COOKIE_NAME, "1");
}

const enableUseTracking = () => {
    return Cookie.set(USE_TRACKING_DISABLED_COOKIE_NAME, "0");
}

const isTrackingOptionSet = () => {
    return Cookie.get(USE_TRACKING_DISABLED_COOKIE_NAME) !== undefined;
}

const isUseTrackingEnabled = () => {
    return Cookie.get(USE_TRACKING_DISABLED_COOKIE_NAME) !== "1";
}

export default {
    USE_TRACKING_DISABLED_COOKIE_NAME,
    disableUseTracking,
    enableUseTracking,
    isUseTrackingEnabled,
    isTrackingOptionSet,
    set: Cookie.set,
    get: Cookie.get,
}
