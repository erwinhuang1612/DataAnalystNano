How Important Is The Time Spent Studying Out Of School
--------------------------

### Abstract
This project is an explanatory data visualization based on [PISA](http://www.oecd.org/pisa/home/) Data Visualization Challenge. The main goal of this project is to explore interesting insights of student grades and the drivers of the grades across the countries. 

### Dataset
PISA is a worldwide study developed by the Organisation for Economic Co-operation and Development (OECD) which examines the skills of 15-year-old school students around the world. 

The study is an assessment of students’ mathematics, science, and reading skills. The dataset contains a insightful information on the background of the students, their school, their grade indicators, and potential attributes affecting the grades. For most of the countries, the sample observation is around 5,000 students, but in some countries the number is even higher. In total, the PISA 2012 dataset contains data on 485,490 pupils.

### Summary
After some preliminary data exploration, I think that there should be some insightful information of "time studied outside of school" as a driver to the maths score of students. In addition, it will also be interesting to visualize the impact of students' social and economy status to their maths score.

There is some initial ideas of visualization that I try to brainstorm through sketching as shown in [first and second version of design](https://github.com/erwinhuang1612/DataAnalystNano/blob/master/DataAnalystNano/P6%20Data%20Visualization/Sketch%20Design.pdf). However, after further data exploration, I have excluded the GDP dimension as I think that it does not support the key insights well. On the other hand, I have included Continent/Country and Economy/Social Index to facilitate the drill of the key insights.

As the dataset is huge, there are some pre-processing done to summarize all the required information, so as to speed up the loading time of the visualization.

### Design
The visualization consists of three charts in a pre-defined position in its order of importance. I have also used pagination concept to facilitate my visual storytelling. 

The boxplot on the left side would be the first view that readers will notice, so it will be the most important as compared to the other charts. The boxplot immediately conveys the key insights: students tend to get higher maths grades when they spend more time studying outside of school time. 

The other charts are to facilitate and to further drilldown the exploration of students grade by economy/social status index and countries. 
By observing and crossfiltering between the bar chart and the boxplot, I can strengthen the key insights by showing that students in higher economy/social status index have better math grades and lower grades for students in lower economy/social status index. I have also made use of highlighting and crossfiltering concept between bar chart and scatterplot to convey the previous point and to make the observation more intuitive.

Interestingly, through the scatterplot, we can observe that there is an exception to the key insights, in which some countries perform reasonably well in spite of relatively lower out-of-school study time.

The pagination allows storyrtelling of the key points mentioned above, so that users are able to comprehend easily the meaning behind the visualization.

### Chart Detail
__Math-score by time studied out-of-school__
This is a box plot to display the distribution of Math Score from OECD dataset across various buckets of out-of-school study time. Boxplot is an ideal visualization here as it summarizeds the huge data points in the data set.

| Variable        | Encoding  |
| ------------- | -----:|
| Hours Studied out of school per week (buckets)       | X-axis |
| Math Score      | Y-axis |
| Median and whiskers values      | labels |


__Number of Students by Social Status Index__
This chart shows the distribution of the data across the social index buckets selected. It also allows cross-filtering between the social index buckets with the math grade distribution by out-of-school study time and country.

| Variable        | Encoding  |
| ------------- | -----:|
| Index of economic, social and cultural status buckets      | X-axis |
| Number of pupils       | Y-axis|

__Average Math Scores by Country vs. Out-of-School Study Time__
In this chart, the user can check more information about each datapoint mousing over the chart. I used a scatter plot here to show the relationship between the two variables enconded here.

| Variable        | Encoding  |
| ------------- | -----:|
| Hours Studied per week       | X-axis |
| Math Score      | Y-axis |
| Math Score,Hours Studied, Continent and Countries names      |   tooltip |
| Continent |    Color Hue |

### Feedback
The __first feedback__ is from a data analytics lecturer/professor. He provides recommendation in the perspective of analytics best-practice. He advised me to make sense of the dataset first by plotting out the relationship between each variable with the key variable first before implementing the sketch design. I followed his advice and realized that GDP does not convey the storytelling well. Thus, excluding this GDP dimension from the visualization. I also included extra country/continent and social index dimension to strengthen the delivery of key insights.

Action taken:
- Excluded GDP dimension
- Included social index and country/continent dimension

The __second feedback__ is from my data analytics manager. He has more business sense and used to sell analytics product, so he likes visualization that are interactive and intuitive. His recommendation is to provide interactivity and cross-filtering across the charts, so that it can strengthen the storytelling of key insights and provides additional interesting insights. On top of that, the cross filtering allows animation and interactivity that makes the visualization more aesthetically appealing and easy to sell.

Action taken:
- Added  cross-filtering from social index bar charts to other charts

The __last feedback__ received is from my colleague, a business user without in-depth data visualization knowledge. In this case, I can test whether the visualization was easy enough for common end-users to understand. He recommends me to add some form of instruction on how to interact/ use the charts on top of the storytelling contents that were shown across the pagination.

Action taken:
- Added textual instruction to facilitate interactivity on the last page of pagination.

### Resources 
- [PISA Data Visualisation Contest](http://beta.icm.edu.pl/PISAcontest/)
- [The Facebook Offering: How It Compares](http://www.nytimes.com/interactive/2012/05/17/business/dealbook/how-the-facebook-offering-compares.html?_r=0)
- [filtering ordinal scale](https://stackoverflow.com/questions/20758373/inversion-with-ordinal-scale/20766269#20766269)
- [a box-plot in D3](http://bl.ocks.org/mbostock/4061502)
- [trend-line in D3](http://bl.ocks.org/benvandyke/8459843)
- [visual enconding](http://www.targetprocess.com/articles/visual-encoding.html)