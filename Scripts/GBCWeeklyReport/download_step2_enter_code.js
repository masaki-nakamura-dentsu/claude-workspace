// GBC週報エクスポート ステップ2: メール認証コードを入力してダウンロードを完了する
// 使い方: node download_step2_enter_code.js <6桁コード>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.GBC_BOT_PORT) || 9231; // d14461では GBC_BOT_PORT=9226 で起動
const CDP_URL = `http://127.0.0.1:${PORT}`;
const DOWNLOAD_DIR = path.join(__dirname, 'downloads');
const STATE_FILE = path.join(__dirname, '.export_state.json');

async function connect() {
  const browser = await chromium.connectOverCDP(CDP_URL);
  const context = browser.contexts()[0];
  return { browser, context };
}

(async () => {
  const code = process.argv[2];
  if (!code) {
    console.log('使い方: node download_step2_enter_code.js <6桁コード>');
    process.exit(1);
  }

  const { context } = await connect();
  const verifyPage = context.pages().find((p) => p.url().includes('identity/verification'));
  if (!verifyPage) {
    console.log('ERROR: 検証タブが見つかりません。download_step1_export.js を先に実行してください。');
    process.exit(1);
  }

  await verifyPage.bringToFront();
  const codeInput = verifyPage.locator('input[type="text"], input[type="tel"], input[name*="code" i]').first();
  await codeInput.fill(code, { timeout: 10000 });

  const submitBtn = verifyPage.getByRole('button', { name: /確認|検証|Verify|Submit|続行/ }).first();
  const [download] = await Promise.all([
    verifyPage.waitForEvent('download', { timeout: 30000 }).catch(() => null),
    submitBtn.click({ timeout: 10000 }),
  ]);

  let dl = download;
  if (!dl) {
    dl = await verifyPage.waitForEvent('download', { timeout: 20000 }).catch(() => null);
  }

  if (!dl) {
    console.log('ダウンロードを検知できませんでした。コードが間違っているか期限切れの可能性があります。');
    process.exit(1);
  }

  if (!fs.existsSync(DOWNLOAD_DIR)) fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
  const fname = `GBC週報_部長会_${new Date().toISOString().slice(0, 10)}.xlsx`;
  const dest = path.join(DOWNLOAD_DIR, fname);
  await dl.saveAs(dest);
  console.log('保存しました:', dest);
  fs.writeFileSync(STATE_FILE, JSON.stringify({ awaitingCode: false, downloadedFile: dest, ts: Date.now() }));
  await verifyPage.close().catch(() => {});
  process.exit(0);
})();
