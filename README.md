==================================================
1. Register Debezium Connectors for DBoth atabases
==================================================

## Register the 'userevents-connector'
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @/debezium-plugins/register-userevents.json

## Register the 'orderevents-connector'
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @/debezium-plugins/register-orderevents.json

## Optional: Delete connectors (for reset/re-register scenarios)
curl -X DELETE http://localhost:8083/connectors/userevents-connector
curl -X DELETE http://localhost:8083/connectors/orderevents-connector


========================================================
2. Verify Kafka Topics Created Automatically by Debezium
========================================================

## List all Kafka topics (to confirm Debezium CDC topics exist)
docker exec -it broker kafka-topics.sh \
  --bootstrap-server broker:9092 \
  --list

## List registered connectors (from inside Kafka Connect container)
docker exec -it debezium curl http://localhost:8083/connectors

## List registered connectors (via REST API)
curl http://localhost:8083/connectors


=========================
3. Delete Kafka CDC Topics
=========================

⚠️ WARNING: Topic deletion is irreversible. Use this only in **development or reset** environments.

# Delete CDC topic for users
docker exec -it broker kafka-topics.sh \
  --bootstrap-server broker:9092 \
  --delete \
  --topic userevents.public.users

# Delete CDC topic for orders
docker exec -it broker kafka-topics.sh \
  --bootstrap-server broker:9092 \
  --delete \
  --topic orderevents.public.orders

========================================
4. Consume Messages from Debezium Topics
========================================

## Read latest messages from 'users' CDC topic
docker exec -it broker kafka-console-consumer.sh \
  --bootstrap-server broker:9092 \
  --topic userevents.public.users

## Read all messages (including history) from 'users' topic
docker exec -it broker kafka-console-consumer.sh \
  --bootstrap-server broker:9092 \
  --topic userevents.public.users \
  --from-beginning

## Read latest messages from 'orders' CDC topic
docker exec -it broker kafka-console-consumer.sh \
  --bootstrap-server broker:9092 \
  --topic orderevents.public.orders

## Read all messages (including history) from 'orders' topic
docker exec -it broker kafka-console-consumer.sh \
  --bootstrap-server broker:9092 \
  --topic orderevents.public.orders \
  --from-beginning


========================================
5. Test Change Data Capture (CDC Events)
========================================

## Modify data in PostgreSQL to generate CDC events

-- In 'userevents' database:
UPDATE public.users
SET address = '999 New Street, Rabat'
WHERE key = 1;

-- In 'orderevents' database:
UPDATE public.orders
SET status = 'shipped'
WHERE id = 1;
