#!/usr/bin/env python3
"""Generate Lab02_Report_21119323.pdf (report skeleton with Q1-Q5 answers).

Evidence screenshots E1-E4 must be captured by the student on their own
Windows machine; placeholder boxes mark where each screenshot goes.
Run:  python make_report.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, grey
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

STUDENT = "Vu Minh Tri"
SID = "21119323"
OUT = os.path.join(os.path.dirname(__file__), f"Lab02_Report_{SID}.pdf")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=14)
muted = ParagraphStyle("muted", parent=body, textColor=grey, fontSize=9)


def placeholder(label):
    """Grey box marking where a screenshot must be inserted."""
    t = Table([[Paragraph(f"[ INSERT SCREENSHOT HERE: {label} ]", styles["Italic"])]],
              colWidths=[16 * cm], rowHeights=[6 * cm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, grey),
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f2f2f2")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


story = [
    Paragraph("Lab 02 — Build and Test a Distributed Client–Server Application", h1),
    Paragraph(f"Student: {STUDENT} — {SID}<br/>Course: Introduction to Cloud Computing<br/>"
              "Environment: Windows · Python 3.10+ · localhost (127.0.0.1:5000)", body),
    Spacer(1, 0.4 * cm),

    Paragraph("1. Source Code Overview", h2),
    Paragraph("<b>server.py</b> binds to 127.0.0.1:5000, accepts connections in a loop, and spawns a "
              "<b>threading.Thread</b> per client. The handler prints the client address and received "
              "message, sleeps for a configurable processing delay (--delay flag, default 2 s), "
              "then echoes the reply back.", body),
    Paragraph("<b>client.py</b> connects to 127.0.0.1:5000 with a 2-second socket timeout, sends "
              "“Hello from client!”, and prints the server’s response. It catches timeouts and "
              "connection errors without crashing, and implements bounded retries: at most 3 attempts "
              "with 0.5 s and 1.0 s waits between them (exponential backoff). Use --no-retry for "
              "single-attempt runs.", body),

    Paragraph("2. Evidence", h2),

    Paragraph("E1 — Basic communication (Task 1)", h2),
    Paragraph("Server terminal shows the client address and received message; client terminal shows "
              "“Server received: Hello from client!”. Both terminals visible in one screenshot.", muted),
    placeholder("E1 — server + client terminals, successful exchange"),

    Paragraph("E2 — Concurrent clients (Task 2)", h2),
    Paragraph("Three client processes started within seconds of each other; all receive responses. The "
              "server log timestamps show overlapping handling (connections accepted before earlier "
              "replies are sent), proving concurrency rather than sequential service.", muted),
    placeholder("E2 — three client outputs + server log with interleaved timestamps"),

    Paragraph("E3 — Timeout experiment (Task 3)", h2),
    Paragraph("Server run with --delay 5 (delay configuration visible); client times out after 2 s and "
              "prints the friendly timeout message while the server process keeps running and eventually "
              "completes its reply. Explanation: a timeout means the response did not arrive within the "
              "client’s deadline — the server may simply be slow or overloaded. The TCP connection was "
              "established and the request was delivered, so the server is demonstrably alive; only the "
              "client gave up waiting.", muted),
    placeholder("E3 — client timeout output + server still running"),

    Paragraph("E4 — Retry experiment (Task 4)", h2),
    Paragraph("With the server stopped, the client logs Attempt 1 failed → wait 0.5 s → Attempt 2 failed "
              "→ wait 1 s → Attempt 3 failed → gives up (bounded, never infinite). After restarting the "
              "server, a normal run succeeds immediately. Retrying a payment or course-registration "
              "request can create duplicates because the first request may have already succeeded on the "
              "server even though its response was lost; an identical retry would then be processed a "
              "second time (double charge / double enrolment).", muted),
    placeholder("E4 — bounded retry log + successful normal run"),

    Paragraph("3. Written Answers (Q1–Q5)", h2),

    Paragraph("Q1. How do the TCP client and server establish a connection and exchange messages?", h2),
    Paragraph("The server binds a socket to 127.0.0.1:5000 and calls listen(). The client calls "
              "connect(), which triggers the TCP three-way handshake (SYN, SYN-ACK, ACK), establishing a "
              "reliable bidirectional byte stream. Afterwards both sides use send()/recv(): the client "
              "sends a request, the server receives it, processes it, and echoes a response back. When "
              "done, close() performs the FIN/ACK teardown. Reliability comes from acknowledgements, "
              "sequencing, and retransmission handled by the TCP layer.", body),

    Paragraph("Q2. What changes when multiple clients are handled concurrently?", h2),
    Paragraph("Instead of accepting one connection, serving it, and then looping, the server spawns a "
              "separate thread per accepted client, so handlers run in parallel. While one thread sleeps "
              "or does slow work, others continue, so total latency no longer accumulates across clients. "
              "New concerns appear: shared state (counters, files) needs locks, log lines interleave, and "
              "each socket must be closed only by its own thread. Concurrency improves throughput but "
              "introduces race-condition risks that single-threaded servers do not have.", body),

    Paragraph("Q3. Why can a client experience a timeout while the server is still running?", h2),
    Paragraph("A timeout is a client-side deadline set with settimeout(); it fires when the expected "
              "response has not arrived in time. The server can still be perfectly alive but slow: heavy "
              "processing, a simulated delay, queueing behind other requests, network congestion, or "
              "packet loss with retransmission. In our lab, a 5-second server delay against a 2-second "
              "client timeout produces exactly this. The request may even complete successfully after the "
              "client gave up, so a timeout indicates “no timely answer”, not “crashed server”.", body),

    Paragraph("Q4. What is the difference between a connection-refused error and a response timeout?", h2),
    Paragraph("Connection refused (WinError 10061 / ConnectionRefusedError) happens during connect(): "
              "the host is reachable but nothing is listening on port 5000, so the OS immediately replies "
              "RST. It usually means the server process is down or the port/address is wrong. A response "
              "timeout happens later: the TCP connection was established successfully, but no answer came "
              "within the deadline. Refusal is fast and proves absence of a listener; a timeout implies "
              "the connection existed and points to slowness, overload, or dropped packets.", body),

    Paragraph("Q5. Why are retry limits and idempotency important in distributed applications?", h2),
    Paragraph("Unlimited retries can hammer a recovering or overloaded server, amplifying failures into a "
              "cascade, and can waste resources forever on permanent errors. Bounded retries with "
              "exponential backoff (0.5 s, 1 s, …) give transient faults time to heal while capping cost. "
              "Idempotency matters because a retry cannot distinguish “request failed” from “response was "
              "lost”: the server may already have applied the operation. Designing operations to be safely "
              "repeatable (read-only queries, idempotency keys for payments) prevents duplicate charges "
              "and registrations.", body),

    Spacer(1, 0.5 * cm),
    Paragraph("Note: replace every grey placeholder box above with your own screenshot before "
              "submitting, then export/re-save this PDF. All screenshots must come from your own "
              "experiments.", muted),
]

# (inline markup already expanded in strings)
for p in story:
    pass

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title=f"Lab02 Report {SID}", author=STUDENT)
doc.build(story)
print("Wrote", OUT)
