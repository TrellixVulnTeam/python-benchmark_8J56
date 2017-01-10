function draw_charts(id, url) {
        $.ajax({
            url: url,
            dataType: "json",
            success: function (data) {
                var title = data.data.title;
                var sub_title = data.data.sub_title;
                var y_axis = data.data.y_axis;
                var unit = data.data.unit;
                var pairs = data.data.pairs;

                var cpu_chart_options = {
                    credits: {
                        enabled: true,
                        text: "© ele.me",
                        href: "https://www.ele.me/home/"
                    },
                    chart: {
                        type: 'column',
                        height: 500
                    },
                    title: {
                        text: title
                    },
                    subtitle: {
                        text: sub_title
                    },
                    xAxis: {
                        type: 'category',
                        labels: {
                            rotation: -45,
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            },
                            formatter: function () {
                                var val = this.value;
                                var return_val = this.value;
                                var n = 12; // one line length
                                if(val.length > n){
                                    return_val = val.substr(0,n)+"<br/>"+val.substr(n,val.length-1);
                                }
                                return return_val
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: y_axis
                        },
                        opposite: false,
                        showEmpty: false
                    },
                    legend: {
                        enabled: false
                    },
                    series: [{
                        name: title,
                        data: pairs,
                        dataLabels: {
                            enabled: true,
                            rotation: 0,
                            color: '#FFFFFF',
                            align: 'center',
                            format: '{point.y:.0f}', // one decimal: {point.y:.1f}
                            y: 26, // 10 pixels down from the top
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        }
                    }],
                    tooltip: {
                        pointFormat: '<b>{point.y:.0f} '+ unit +'</b>'
                    }
                };


                $(id).highcharts(cpu_chart_options)
            },
            cache: false

        });
}