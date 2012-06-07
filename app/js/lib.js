/**
 * Calculate the difference between two dates.
 * @param Date date1 the first date
 * @param Date date2 the second date
 * @return the differnce between two dates in number of days.
 */
function differenceInDays(date1, date2) {
	var millisBetween = Math.abs(date2.getTime() - date1.getTime());
	var millisecondsPerDay = 1000 * 60 * 60 * 24;
	var daysRemaining = Math.ceil(millisBetween / millisecondsPerDay);
	
	return daysRemaining;
}

function numericOnly(evt)
{
	evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
	
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false
    }
    return true
}