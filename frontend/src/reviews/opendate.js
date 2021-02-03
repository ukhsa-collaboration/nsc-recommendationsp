import moment from 'moment'

export const opendate = () => {
    const startDayName = 'consultation_start_day'
    const startMonthName = 'consultation_start_month'
    const startYearName = 'consultation_start_year'
    const endDayName = 'consultation_end_day'
    const endMonthName = 'consultation_end_month'
    const endYearName = 'consultation_end_year'

    const startDayElem = document.getElementsByName(startDayName)[0]
    const startMonthElem = document.getElementsByName(startMonthName)[0]
    const startYearElem = document.getElementsByName(startYearName)[0]
    const endDayElem = document.getElementsByName(endDayName)[0]
    const endMonthElem = document.getElementsByName(endMonthName)[0]
    const endYearElem = document.getElementsByName(endYearName)[0]

    const updateEndDate = () => {
        const startDate = moment([startYearElem.value, startMonthElem.value - 1, startDayElem.value])
        if (startDate.format() === "Invalid date") {
            return
        }

        const targetEndDate = startDate.clone().add(3, 'months')
        if(endDayElem) {endDayElem.value = targetEndDate.date()}
        if(endMonthElem) {endMonthElem.value = targetEndDate.month() + 1}
        if(endYearElem) {endYearElem.value = targetEndDate.year()}
    }

    // setup the event listeners
    if (startDayElem) {startDayElem.addEventListener('change', updateEndDate)}
    if (startMonthElem) {startMonthElem.addEventListener('change', updateEndDate)}
    if (startYearElem) {startYearElem.addEventListener('change', updateEndDate)}
}
