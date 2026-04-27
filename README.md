<div align="center">

# Mohammed Saifulhuq

**Backend Engineer · Distributed Systems · Open Source Builder**

[![Portfolio](https://img.shields.io/badge/Portfolio-saifulhuq.vercel.app-00d4aa?style=for-the-badge&logo=vercel&logoColor=white)](https://saifulhuq.vercel.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-saifulhuqs-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/saifulhuqs)
[![Gmail](https://img.shields.io/badge/Gmail-mohammed.saifulhuq-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mohammed.saifulhuq@gmail.com)

</div>

---

```
root@saifulhuq:~$ cat status.log
```

```
[ACTIVE]   Building DLQ Revive — open-source Kafka DLQ recovery engine
[ACTIVE]   Contributing to Apache Fineract — core banking platform
[OPEN]     Available for backend/distributed systems roles
[STACK]    Java 17 · Spring Boot 3 · Apache Kafka · Angular 13+ · PostgreSQL
```

---

### `🚀 current_build: DLQ Revive`

> When Kafka consumers fail due to schema changes, messages pile up in Dead Letter Queues.  
> Every team writes a throwaway script. No one built the tool. So I built it.

```diff
+ Browse    — Paginated DLQ inspection. Never loads full topic into memory.
+ Transform — JSONata expression engine. No Groovy. No RCE surface.
+ Preview   — Before/after schema diff before touching production.
+ Redrive   — Idempotency guard at (topic, partition, offset) level.
+             Pod-restart safe. Zero double-processing.
+ Audit     — Every action logged to PostgreSQL with full traceability.
```

**Validated by 4 senior Kafka engineers on r/apachekafka. 63K+ LinkedIn reach. MIT licensed.**

<div align="center">

[![DLQ Revive](https://img.shields.io/badge/dlq--revive-View_Project-00d4aa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Saifulhuq01/dlq-revive)
[![License: MIT](https://img.shields.io/badge/License-MIT-00d4aa?style=for-the-badge)](https://github.com/Saifulhuq01/dlq-revive/blob/main/LICENSE)

</div>

---

### `🛡️ open_source.log — Apache Fineract`

Production contributor to Apache Fineract — open-source core banking platform used for financial inclusion globally.

```diff
+ SECURITY  — Patched critical SQL Injection in lending engine. PR #5465 merged.
+             100% green CI across PostgreSQL, MariaDB, MySQL.
+ IDEMPOTENCY — Architecting system-wide transaction idempotency interceptor (FINERACT-2485).
+              OncePerRequestFilter + PostgreSQL INSERT ... ON CONFLICT DO NOTHING.
+              Eliminates exception-driven control flow on the critical execution path.
+ CI/CD     — Resolved Liquibase migration failures for strict PostgreSQL type compliance.
```

<div align="center">

[![Apache Fineract PRs](https://img.shields.io/badge/Merged_PRs-Apache_Fineract-FF4500?style=for-the-badge&logo=apache&logoColor=white)](https://github.com/apache/fineract/pulls?q=is%3Apr+author%3ASaifulhuq01+is%3Amerged)

</div>

---

### `🛠️ tech_stack.conf`

| Domain | Technologies |
| :--- | :--- |
| **Backend** | ![Java](https://img.shields.io/badge/Java_17-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white) ![Spring Boot](https://img.shields.io/badge/Spring_Boot_3-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white) |
| **Messaging** | ![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white) |
| **Frontend** | ![Angular](https://img.shields.io/badge/Angular_13+-DD0031?style=for-the-badge&logo=angular&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white) ![RxJS](https://img.shields.io/badge/RxJS-B7178C?style=for-the-badge&logo=reactivex&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white) |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) ![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white) |

---

### `⚙️ core_principles.conf`

```yaml
production_safety:
  rule: "Code must survive pod restarts, concurrent requests, and schema drift."
  example: "UNIQUE(topic, partition, offset) — not application-level checks."

security_by_design:
  rule: "Never allow Turing-complete user input on the server."
  example: "JSONata over Groovy. Declarative over executable."

kafka_consumer_hygiene:
  rule: "Read-only consumers must never join consumer groups."
  example: "assign()+seek() — not subscribe(). Never commitSync() in view mode."

open_source_first:
  rule: "Build in public. Validate before building. Ship before perfecting."
```

---

### `📊 system_metrics`

<div align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=Saifulhuq01&show_icons=true&theme=radical&hide_border=true&bg_color=0d1117&title_color=00d4aa&icon_color=00d4aa&text_color=c9d1d9" height="170" alt="stats" />
  &nbsp;&nbsp;
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Saifulhuq01&layout=compact&theme=radical&hide_border=true&bg_color=0d1117&title_color=00d4aa&text_color=c9d1d9" height="170" alt="languages" />
</div>

<br/>

<div align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com?user=Saifulhuq01&theme=radical&hide_border=true&background=0d1117&ring=00d4aa&fire=00d4aa&currStreakLabel=00d4aa" height="170" alt="streak" />
</div>

---

<div align="center">

```
root@saifulhuq:~$ uptime
 status: BUILDING_IN_PUBLIC — week: 2 — product: dlq-revive — target: launch
```

<sub>⚡ Production-grade code or nothing ⚡</sub>

</div>
