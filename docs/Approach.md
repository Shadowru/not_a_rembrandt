1. Общий подход
Система состоит из четырех основных компонентов:

Collector Agent (Сборщик): Работает внутри или снаружи кластера, собирает сырые данные.
Graph Logic Processor (Анализатор): Обрабатывает данные, строит связи, обогащает метаданными (Swagger/OpenAPI) и пишет в БД.
Graph Database (Хранилище): Хранит топологию (Neo4j, ArangoDB).
C4 Generator Service (Генератор): API для генерации диаграмм (PlantUML, Structurizr DSL, Mermaid) на основе запросов к графу.

2. Детальное проектирование компонентов

2.1. Collector Agent (Сборщик)

Написан на Go (лучшая поддержка k8s client-go).


Задачи:


Static Discovery: Опрос K8s API (Deployments, Services, Ingress, ConfigMaps, NetworkPolicies).
Dynamic Discovery (Связи):
Вариант А (Service Mesh): Если есть Istio/Linkerd, опрашиваем Prometheus для получения метрик
source -> destination
. Это самый точный способ построения графа зависимостей.
Вариант Б (Heuristics): Парсинг переменных окружения (ENV) в подах. Ищем строки, похожие на URL других сервисов внутри кластера.
Вариант В (eBPF): Использование eBPF (например, через Cilium Hubble или Pixie) для перехвата сетевых вызовов без sidecar-ов.
API Discovery: Попытка стянуть
/openapi.json
или
/swagger.json
с сервисов (через port-forward или внутрикластерный доступ) для понимания методов.

2.2. Graph Logic Processor (Анализатор)

Это "мозг" системы. Он преобразует ресурсы K8s в сущности графа.


Логика маппинга (K8s -> C4):


Namespace -> C4 System Boundary (или Software System).
Deployment / StatefulSet -> C4 Container (Приложение/Микросервис).
Service / Ingress -> Интерфейсы взаимодействия.
Database (RDS/StatefulSet) -> C4 Container (Database).
External Service (ExternalName) -> C4 Software System (External).

Логика построения ребер (Edges):


Если Ingress указывает на Service A ->
User USES Service A
.
Если Service A вызывает Service B (по данным Mesh/eBPF) ->
Service A USES Service B
.
Если Pod A имеет ENV
DB_HOST=postgres
->
Service A USES Postgres
.

2.3. Graph Database (Схема данных)

Узлы (Nodes/Labels):
:Cluster
{name, region}
:Namespace
{name}
:App
{name, type: "service"|"db"|"queue", language, replicas}
:Endpoint
{path, method, protocol} (извлечено из Ingress или OpenAPI)
:Infrastructure
{type: "node", ip, capacity}

Связи (Relationships):


(:Namespace)-[:CONTAINS]->(:App)
(:App)-[:EXPOSES]->(:Endpoint)
(:App)-[:CALLS {frequency, latency}]->(:App)
(:App)-[:USES]->(:Database)
(:Ingress)-[:ROUTES_TO]->(:App)

2.4. C4 Generator Service

Сервис на Python или Go, который принимает параметры (например, "Дай мне уровень Container для Namespace X") и генерирует код.

Форматы вывода:

Structurizr DSL (рекомендуемый): Текстовый формат, который легко конвертируется в JSON, PNG, SVG и интерактивные UI.
Mermaid / PlantUML: Для быстрого рендеринга в документации (Markdown).
