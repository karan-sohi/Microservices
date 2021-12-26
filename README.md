# Microservices

There are total 5 micro-services 
- Receiver - The receiver service receives the requests (orders) from the clients, and publish them to the Kafka topic. 
- Storage - The storage service consume messages from Kafka topic and store them to the MySQL database. 
- Processing - The processing service leverages periodic processing by retreiving the data from the storage service with GET endpoints and store it into a JSON file. 
- Audit Log Service - The Audit Log service receive index as GET API endpoints from clients, and return the events at that index relative to the beginnning of Kafka message queue. 
- Dashboard UI - The dashboard UI service displays the current statistics and audit information by calling API endpoints from the Processing and Audit Log service. 

![Infrastructure](https://github.com/karan-sohi/Microservices/blob/main/images/front_back%20infrastructure.png)

## NGINX Load Balancer 
The Nginx load balancer is used to enable scaling up the storage and receiver services by increasing the number of containers according to the traffic. All the API endpoints between the services goes through the load balancer to enable the scalability of servcies. 

![Infrastructure](https://github.com/karan-sohi/Microservices/blob/main/images/Infrastructure.png)



