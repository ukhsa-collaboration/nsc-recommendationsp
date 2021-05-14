import Cookies from "../utils/cookies"

const initCookieBanner = () => {
    const rootElement = document.getElementById("cookie-banner")
    const formElement = document.getElementById("cookie-banner-form")
    const questionElement = document.getElementById("cookie-banner-question")
    const questionAnsweredElement = document.getElementById("cookie-banner-answered")
    const acceptedMessageElement = document.getElementById("cookie-banner-accepted-message")
    const rejectedMessageElement = document.getElementById("cookie-banner-rejected-message")

    // set the initial hidden states
    const bannerHidden = Cookies.get("cookieBannerHidden") === "1"
    rootElement.hidden = bannerHidden
    questionElement.hidden = Cookies.isTrackingOptionSet()
    questionAnsweredElement.hidden = !Cookies.isTrackingOptionSet()
    acceptedMessageElement.hidden = !Cookies.isUseTrackingEnabled()
    rejectedMessageElement.hidden = Cookies.isUseTrackingEnabled()

    formElement.addEventListener("submit", (e) => {
        e.preventDefault()

        if(e.submitter.value === "accept") {
            questionElement.hidden = true
            questionAnsweredElement.hidden = false
            acceptedMessageElement.hidden = false
            rejectedMessageElement.hidden = true
            Cookies.enableUseTracking()
        } else if (e.submitter.value === "reject") {
            questionElement.hidden = true
            questionAnsweredElement.hidden = false
            acceptedMessageElement.hidden = true
            rejectedMessageElement.hidden = false
            Cookies.disableUseTracking()
        } else if (e.submitter.value === "hide") {
            rootElement.hidden = true
            Cookies.set("cookieBannerHidden", "1")
        }
    })
}

export {
    initCookieBanner
}
