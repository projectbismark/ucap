/**
 * Grid theme for Highcharts JS
 * @author Torstein Hønsi
 */

Highcharts.theme = {
	colors: ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"],
    //alternate - "#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2", "#31a354", "#74c476", "#a1d99b", "#c7e9c0", "#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb", "#636363", "#969696", "#bdbdbd", "#d9d9d9"
	chart: {
		borderWidth: 0,
		plotBackgroundColor: 'rgba(255, 255, 255, .9)',
		plotShadow: false,
		plotBorderWidth: 0
	},
	title: {
		style: {
			color: '#000',
			font: 'bold 16px "PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'
		}
	},
	subtitle: {
		style: {
			color: '#666666',
			font: 'bold 12px "PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'
		}
	},
	xAxis: {
		gridLineWidth: 1,
		lineColor: '#999999',
		tickColor: '#888888',
		labels: {
			style: {
				color: '#646464',
				font: '11px "PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'
			}
		},
		title: {
			style: {
				color: '#333',
				fontWeight: 'bold',
				fontSize: '12px',
				fontFamily: '"PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'

			}
		}
	},
	yAxis: {
		minorTickInterval: 'auto',
		lineColor: '#999999',
		lineWidth: 1,
		tickWidth: 1,
		tickColor: '#888888',
		labels: {
			style: {
				color: '#646464',
				font: '11px "PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'
			}
		},
		title: {
			style: {
				color: '#777',
				fontWeight: 'bold',
				fontSize: '12px',
				fontFamily: '"PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif'
			}
		}
	},
	legend: {
		itemStyle: {
			font: '9pt "PT Sans","Arial","Helvetica","Lucida Grande","Gill Sans","Verdana",sans-serif',
			color: '#545454'
		},
		itemHoverStyle: {
			color: '#1155CC'
		},
		itemHiddenStyle: {
			color: '#888'
		},
        borderWidth:0,
        borderColor:'#FFFFFF'
	},
	labels: {
		style: {
			color: '#99b'
		}
	}
};

// Apply the theme
var highchartsOptions = Highcharts.setOptions(Highcharts.theme);
