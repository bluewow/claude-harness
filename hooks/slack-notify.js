#!/usr/bin/env node
/**
 * .claude/hooks/slack-notify.js
 *
 * Claude Code hook — Slack notification
 * Events: Stop, Notification, PreToolUse(AskUserQuestion)
 *
 * Webhook URL 설정:
 *   .claude/settings.local.json → env.SLACK_WEBHOOK_URL
 */

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  try {
    main(JSON.parse(input));
  } catch {
    process.exit(0);
  }
});

// ── Main ──────────────────────────────────────────────

function main(data) {
  const webhookUrl = getWebhookUrl(data.cwd);
  if (!webhookUrl) return;

  const project = path.basename(data.cwd || "unknown");
  const event = data.hook_event_name;

  const payload = buildPayload(event, project, data);
  if (!payload) return;

  sendSlack(webhookUrl, payload);
}

// ── Helpers ───────────────────────────────────────────

function timestamp() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");
  return `${h}:${m}`;
}

function truncate(str, max) {
  if (!str) return "";
  return str.length > max ? str.slice(0, max) + "..." : str;
}

// ── Payload builders ──────────────────────────────────

function buildPayload(event, project, data) {
  if (event === "Stop") {
    return stopPayload(project, data);
  }
  if (event === "Notification") {
    return notificationPayload(project, data);
  }
  if (event === "PreToolUse") {
    return preToolUsePayload(project, data);
  }
  return null;
}

function stopPayload(project, data) {
  const reason = data.stop_reason || "end_turn";
  if (reason !== "end_turn") return null;

  const transcript = data.transcript || [];

  // 마지막 assistant 메시지에서 요약 추출
  let lastMessage = "";
  for (let i = transcript.length - 1; i >= 0; i--) {
    const msg = transcript[i];
    if (msg.role === "assistant") {
      if (typeof msg.content === "string") {
        lastMessage = msg.content;
      } else if (Array.isArray(msg.content)) {
        const textBlock = msg.content.find((b) => b.type === "text");
        if (textBlock) lastMessage = textBlock.text;
      }
      break;
    }
  }

  const summary = truncate(lastMessage, 200) || "작업이 완료되었습니다.";

  return {
    text: `[${project}] 작업 완료`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `:white_check_mark:  ${project}`,
          emoji: true,
        },
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: summary,
        },
      },
      {
        type: "context",
        elements: [
          {
            type: "mrkdwn",
            text: `${timestamp()}  |  작업 완료`,
          },
        ],
      },
    ],
  };
}

function notificationPayload(project, data) {
  const message = data.message || "확인이 필요합니다.";

  return {
    text: `[${project}] ${message}`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `:bell:  ${project}`,
          emoji: true,
        },
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: message,
        },
      },
      {
        type: "context",
        elements: [
          {
            type: "mrkdwn",
            text: `${timestamp()}  |  알림`,
          },
        ],
      },
    ],
  };
}

function preToolUsePayload(project, data) {
  const toolName = data.tool_name || "unknown";
  if (toolName !== "AskUserQuestion") return null;

  const toolInput = data.tool_input || {};
  const questions = toolInput.questions || [];

  // 질문 + 선택지 포맷
  const lines = [];
  questions.forEach((q, i) => {
    const prefix = questions.length > 1 ? `*${i + 1}.* ` : "";
    lines.push(`${prefix}${q.question || ""}`);

    if (q.options && q.options.length > 0) {
      q.options.forEach((opt) => {
        const desc = opt.description ? `  _${opt.description}_` : "";
        lines.push(`    :small_blue_diamond: ${opt.label}${desc}`);
      });
    }
  });

  const body = lines.length > 0 ? lines.join("\n") : "질문이 있습니다.";

  return {
    text: `[${project}] 응답 필요`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `:raising_hand:  ${project}`,
          emoji: true,
        },
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: body,
        },
      },
      {
        type: "context",
        elements: [
          {
            type: "mrkdwn",
            text: `${timestamp()}  |  응답 대기 중`,
          },
        ],
      },
    ],
  };
}

// ── Webhook URL ───────────────────────────────────────

function getWebhookUrl(cwd) {
  // 1. Environment variable
  if (process.env.SLACK_WEBHOOK_URL) return process.env.SLACK_WEBHOOK_URL;

  // 2. .claude/settings.local.json
  if (cwd) {
    try {
      const p = path.join(cwd, ".claude", "settings.local.json");
      const cfg = JSON.parse(fs.readFileSync(p, "utf8"));
      if (cfg.env?.SLACK_WEBHOOK_URL) return cfg.env.SLACK_WEBHOOK_URL;
    } catch {
      // fall through
    }
  }

  // 3. Script 위치 기준 (복사 시 대비)
  try {
    const p = path.join(__dirname, "..", "settings.local.json");
    const cfg = JSON.parse(fs.readFileSync(p, "utf8"));
    if (cfg.env?.SLACK_WEBHOOK_URL) return cfg.env.SLACK_WEBHOOK_URL;
  } catch {
    // fall through
  }

  return "";
}

// ── HTTP ──────────────────────────────────────────────

function sendSlack(webhookUrl, payload) {
  const url = new URL(webhookUrl);
  const body = JSON.stringify(payload);

  const options = {
    hostname: url.hostname,
    port: url.port || (url.protocol === "https:" ? 443 : 80),
    path: url.pathname + url.search,
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(body),
    },
  };

  const transport = url.protocol === "https:" ? https : http;
  const req = transport.request(options);
  req.on("error", () => {}); // silent
  req.write(body);
  req.end();
}
