# cs6422_project : Quantifying state staleness in a distributed resource management control plane
<br />

Introduction
<br />
Problem
We take a mathematical approach to analyze various state synchronization techniques used by the distributed control-plane. For the sake of tractability we break the problem down into two settings : single-controller and multicontroller settings. 
Why is this problem important?
-There is no standard for deployment of edge computing systems, hence there is no consensus about the flavor of control plane state management solutions will be ideal. 
-The analysis in this project will enable us to reason the pros and cons of a specific control plane design based on the properties like latency distribution of a given edge computing deployment.
<br />
solution
<br />
75% goal completed: 
<br />

100% goal (underway)
- Formulate the probability of staleness/transaction failure for multi-controller setting
- Implement a Monte Carlo simulation (based on PBS source code) and generate behavior of the staleness probability with respect to the independent variables like controller-server latency, inter-controller latency.
<br />

125% goal
- Implementation of single and multi controller designs for a Docker cluster
- Infrastructure emulation to mimic edge-computing setting
- Correlate with results from the models built earlier
<br />

Contributions:<br />

-mathematical model-report-presentation : team<br />
-single simulator integrations :  Harshit<br />
-2pc commit : Lucia<br />
-communications : Salini
