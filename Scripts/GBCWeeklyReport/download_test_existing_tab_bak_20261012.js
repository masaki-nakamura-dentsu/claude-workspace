// テスト用: 既に開いている(ユーザーが過去20日にフィルタを広げた)タブに対してエクスポートを実行する
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.GBC_BOT_PORT) || 9227; // d14461では GBC_BOT_PORT=9226 で起動
const CDP_URL = `http://127.0.0.1:${PORT}`;
const DOWNLOAD_DIR = path.join(__dirname, 'downloads');
const STATE_FILE = path.join(__dirname, '.export_state.json');

async function connect() {
  const browser = await chromium.connectOverCDP(CDP_URL);
  const context = browser.contexts()[0];
  return { browser, context };
}

(async () => {
  if (!fs.existsSync(DOWNLOAD_DIR)) fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });

  const { context } = await connect();
  const page = context.pages().find((p) => p.url().includes('AmEiQUAV'));
  if (!page) { console.log('ERROR: 対象タブが見つかりません'); process.exit(1); }
  await page.bringToFront();

  const frame = page.frames().find((f) => f.url().includes('lightningReportApp'));
  if (!frame) { console.log('ERROR: フレームが見つかりません'); process.exit(1); }

  const moreBtn = frame.getByRole('button', { name: /追加アクション/ }).first();
  await moreBtn.click({ timeout: 15000 });
  await page.waitForTimeout(800);
  await frame.getByText('エクスポート', { exact: true }).click({ timeout: 10000 });
  await page.waitForTimeout(2000);

  const exportConfirmBtn = page.getByRole('button', { name: 'エクスポート', exact: true }).last();
  await exportConfirmBtn.click({ timeout: 15000 });
  console.log('エクスポート確認ボタンをクリックしました。検証タブの出現を待ちます...');
  await page.waitForTimeout(4000);

  const pages = context.pages();
  const verifyPage = pages.find((p) => p.url().includes('identity/verification'));

  if (verifyPage) {
    console.log('メール認証コードが必要です。masaki.nakamura@dentsu.co.jp 宛のメールを確認し、');
    console.log('  node download_step2_enter_code.js <6桁コード>');
    console.log('を実行してください。');
    fs.writeFileSync(STATE_FILE, JSON.stringify({ awaitingCode: true, ts: Date.now() }));
    process.exit(0);
  }

  console.log('検証タブなし。直接ダウンロードを試みます...');
  try {
    const download = await page.waitForEvent('download', { timeout: 20000 });
    const fname = `GBC週報_部長会_TEST_${new Date().toISOString().slice(0, 10)}.xlsx`;
    const dest = path.join(DOWNLOAD_DIR, fname);
    await download.saveAs(dest);
    console.log('保存しました:', dest);
    fs.writeFileSync(STATE_FILE, JSON.stringify({ awaitingCode: false, downloadedFile: dest, ts: Date.now() }));
  } catch (e) {
    console.log('ダウンロードイベントを検知できませんでした:', e.message);
  }

  process.exit(0);
})();
