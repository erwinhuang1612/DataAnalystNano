"use strict";

//************************************************************
// begin of help functions
//************************************************************

function displayUdacity(s_type){
     /**
     * hide (show another chart) and show udacity bar chart
     */
    if(s_type=="show"){
        d3.select("#FirstChart").attr("style","display:inline;");
        d3.select("#SecondChart").attr("style","display:none;");
    } 
    else{
        d3.select("#FirstChart").attr("style","display:none;");
        d3.select("#SecondChart").attr("style","display:inline;");
    }
    
}


//draw the bar chart
function draw_udacity() {
     /**
     * load data/udacity_time.csv and call renderChart function
     */    

    //create function to parse date
    var formatTime = d3.time.format("%Y-%m-%d");

    //Fetcching data
    var fr_data = "data/udacity_time.csv"
    d3.csv(fr_data, function (error, data) {
        //redefine the format of the data
        data.forEach(function(d){
            d.DATE= formatTime.parse(d.DATE);
            d.MINT= +d.MINT;

            return d;
            }),
        //render the data
        renderChart(data)
        }
    );  

}