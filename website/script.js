// ── Theme ──
(function() {
  const stored = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = stored || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

// ── Reveal on scroll ──
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
});

// ── Counter Animation ──
function animateCounter(el, target, suffix = '') {
  const isFormatted = typeof target === 'string' && target.includes('+');
  const num = parseInt(target);
  let current = 0;
  const step = Math.max(1, Math.floor(num / 60));
  const timer = setInterval(() => {
    current += step;
    if (current >= num) {
      current = num;
      clearInterval(timer);
    }
    el.textContent = (isFormatted ? current.toLocaleString() + '+' : current.toLocaleString()) + suffix;
  }, 20);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = el.getAttribute('data-count');
      if (target) {
        const suffix = el.getAttribute('data-suffix') || '';
        animateCounter(el, target, suffix);
      }
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));
});

// ── Demo Simulator ──
const demoData = {
  tasks: [
    {
      label: 'Plot CSV chart',
      steps: [
        { log: 'Scanning workspace for CSV files...', pct: 8 },
        { log: 'Found: sales_data.csv (2.4MB)', pct: 15 },
        { log: 'Planning: load, parse, aggregate, plot', pct: 22 },
        { log: 'Tool selected: PandasTool, MatplotlibTool', pct: 30 },
        { log: 'Writing Python script...', pct: 42 },
        { log: 'Auditor: reviewing for destructive ops', pct: 55 },
        { log: 'Auditor: ALLOW — safe operations only', pct: 65 },
        { log: 'Executing: python plot_csv.py', pct: 78 },
        { log: 'Output: chart saved to chart_output.png', pct: 90 },
        { log: 'Verifier: checking output exists & matches task', pct: 96 },
        { log: '✓ Task complete. Chart generated successfully.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Plot a chart from my CSV file' },
        { role: 'agent', text: 'I\'ll analyze your CSV and generate a chart. Let me start by scanning for CSV files in your workspace.' },
        { role: 'agent', text: 'Found sales_data.csv with columns: Date, Product, Revenue, Quantity. I\'ll aggregate revenue by month and plot a bar chart.' },
        { role: 'agent', text: 'Script generated (42 lines). Auditor has reviewed and approved it. No destructive operations detected.' },
        { role: 'agent', text: '✓ Done! Chart saved to chart_output.png — a clean bar chart of monthly revenue with proper labels.' },
      ]
    },
    {
      label: 'Rename 100 files',
      steps: [
        { log: 'Scanning target directory...', pct: 6 },
        { log: 'Found 127 files matching pattern', pct: 14 },
        { log: 'Planning: bulk rename with prefix "invoice_"', pct: 24 },
        { log: 'Tool selected: FileSystemTool, BatchRenameTool', pct: 33 },
        { log: 'Writing Python rename script...', pct: 44 },
        { log: 'Auditor: reviewing for data loss risk', pct: 56 },
        { log: 'Auditor: ALLOW — reversible naming pattern', pct: 65 },
        { log: 'Executing: python batch_rename.py', pct: 76 },
        { log: 'Renamed 100/100 files in 0.8s', pct: 88 },
        { log: 'Verifier: checking all files renamed correctly', pct: 95 },
        { log: '✓ 100 files renamed. invoice_001.pdf → invoice_100.pdf', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Rename all PDFs numerically' },
        { role: 'agent', text: 'Scanning your Documents folder for PDF files...' },
        { role: 'agent', text: 'Found 100 PDF files. I\'ll rename them as invoice_001.pdf through invoice_100.pdf.' },
        { role: 'agent', text: 'Script ready. Auditor has reviewed and approved it.' },
        { role: 'agent', text: '✓ All 100 files renamed successfully in under a second!' },
      ]
    },
    {
      label: 'Scrape → Excel',
      steps: [
        { log: 'Planning web scrape task...', pct: 5 },
        { log: 'Tool selected: RequestsTool, BeautifulSoupTool', pct: 15 },
        { log: 'Writing Python scraper...', pct: 28 },
        { log: 'Auditor: reviewing external requests', pct: 40 },
        { log: 'Auditor: ALLOW — read-only HTTP GET', pct: 50 },
        { log: 'Executing: python scrape_to_excel.py', pct: 62 },
        { log: 'Fetched 200 records from target page', pct: 75 },
        { log: 'Writing to Excel with formatting...', pct: 85 },
        { log: 'Verifier: checking Excel file integrity', pct: 94 },
        { log: '✓ Data saved to scrape_results.xlsx', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Scrape website data to Excel' },
        { role: 'agent', text: 'I\'ll build a scraper that extracts data and saves it as a formatted Excel file.' },
        { role: 'agent', text: 'Target URL is accessible. Extracting table data from the page...' },
        { role: 'agent', text: '200 records extracted. Writing to Excel with auto-sized columns and headers.' },
        { role: 'agent', text: '✓ Done! scrape_results.xlsx is ready with 200 records.' },
      ]
    },
    {
      label: 'Bulk email from CSV',
      steps: [
        { log: 'Scanning for CSV with email contacts...', pct: 7 },
        { log: 'Found: contacts.csv (53 recipients)', pct: 16 },
        { log: 'Planning: read CSV, compose, send via SMTP', pct: 26 },
        { log: 'Tool selected: SMTPAdvancedTool, CSVTool', pct: 35 },
        { log: 'Writing Python email script...', pct: 46 },
        { log: 'Auditor: reviewing for sensitive data exposure', pct: 57 },
        { log: 'Auditor: ALLOW — no sensitive fields in CSV', pct: 66 },
        { log: 'Executing: python bulk_email.py', pct: 77 },
        { log: 'Sent: 53/53 emails delivered', pct: 88 },
        { log: 'Verifier: checking delivery reports', pct: 95 },
        { log: '✓ All 53 emails sent successfully.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Send bulk emails from CSV' },
        { role: 'agent', text: 'Reading your contacts.csv to prepare the email campaign...' },
        { role: 'agent', text: 'Found 53 recipients with Name, Email, Company columns.' },
        { role: 'agent', text: 'Script ready. Auditor approved. Sending personalized emails now...' },
        { role: 'agent', text: '✓ All 53 emails sent and delivered successfully!' },
      ]
    },
    {
      label: 'Open a GitHub issue',
      steps: [
        { log: 'Checking GitHub authentication...', pct: 8 },
        { log: 'Authenticated as @user', pct: 18 },
        { log: 'Plan: repo lookup, issue create with labels', pct: 28 },
        { log: 'Tool selected: GitHubTool', pct: 36 },
        { log: 'Writing Python script...', pct: 46 },
        { log: 'Auditor: reviewing repo write access', pct: 56 },
        { log: 'Auditor: ALLOW — issue creation only', pct: 64 },
        { log: 'Executing: python create_issue.py', pct: 74 },
        { log: 'Issue #42 created in target repo', pct: 86 },
        { log: 'Verifier: confirming issue exists via API', pct: 94 },
        { log: '✓ Issue opened: github.com/org/repo/issues/42', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'File a GitHub issue about bug' },
        { role: 'agent', text: 'Connecting to GitHub API... Authenticated successfully.' },
        { role: 'agent', text: 'I\'ve written a detailed bug report with reproduction steps, expected vs actual behavior, and environment info.' },
        { role: 'agent', text: 'Auditor has reviewed — safe. Creating the issue now...' },
        { role: 'agent', text: '✓ Issue #42 created with bug label and priority: medium.' },
      ]
    },
    {
      label: 'Zip & sort PDFs',
      steps: [
        { log: 'Scanning Documents/PDFs...', pct: 6 },
        { log: 'Found 45 PDF files in 3 folders', pct: 16 },
        { log: 'Plan: sort by date, zip with folders', pct: 26 },
        { log: 'Tool selected: ZipTool, FileSystemTool', pct: 34 },
        { log: 'Writing Python archiver...', pct: 44 },
        { log: 'Auditor: reviewing file organization safety', pct: 54 },
        { log: 'Auditor: ALLOW — non-destructive archiving', pct: 62 },
        { log: 'Executing: python archive_pdfs.py', pct: 72 },
        { log: 'Created: PDFs_Archive_2024.zip (128MB)', pct: 84 },
        { log: 'Verifier: checking archive integrity', pct: 94 },
        { log: '✓ 45 PDFs sorted & archived.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Zip and organize my PDFs' },
        { role: 'agent', text: 'Scanning your Documents folder for PDF files scattered across directories...' },
        { role: 'agent', text: 'Found 45 PDFs. I\'ll sort them by date and create a well-organized archive.' },
        { role: 'agent', text: 'Archive created. Auditor verified no files were deleted — only copied.' },
        { role: 'agent', text: '✓ PDFs_Archive_2024.zip ready with 45 files sorted into folders.' },
      ]
    },
    {
      label: 'List S3 objects',
      steps: [
        { log: 'Checking AWS credentials...', pct: 6 },
        { log: 'AWS credentials valid', pct: 16 },
        { log: 'Plan: list buckets, enumerate objects', pct: 26 },
        { log: 'Tool selected: AWSS3Tool', pct: 34 },
        { log: 'Writing Python S3 script...', pct: 44 },
        { log: 'Auditor: reviewing S3 read operations', pct: 54 },
        { log: 'Auditor: ALLOW — read-only S3 operations', pct: 62 },
        { log: 'Executing: python list_s3_objects.py', pct: 72 },
        { log: 'Bucket: my-app-data — 1,240 objects', pct: 84 },
        { log: 'Verifier: confirming object list matches count', pct: 94 },
        { log: '✓ S3 inventory complete. 1,240 objects across 3 buckets.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Show my S3 bucket contents' },
        { role: 'agent', text: 'Authenticating with AWS... Credentials verified successfully.' },
        { role: 'agent', text: 'Found 3 buckets. Listing objects in the primary bucket now.' },
        { role: 'agent', text: 'Script complete. Auditor confirmed read-only access only.' },
        { role: 'agent', text: '✓ my-app-data: 1,240 objects, 3.2GB total across 12 prefixes.' },
      ]
    },
    {
      label: 'Rebuild Docker image',
      steps: [
        { log: 'Checking Docker daemon...', pct: 5 },
        { log: 'Docker daemon running (v24.0.7)', pct: 14 },
        { log: 'Plan: Dockerfile found, rebuild with no-cache', pct: 24 },
        { log: 'Tool selected: DockerTool', pct: 33 },
        { log: 'Writing Docker build script...', pct: 44 },
        { log: 'Auditor: reviewing Dockerfile safety', pct: 54 },
        { log: 'Auditor: ALLOW — standard build', pct: 62 },
        { log: 'Executing: docker build --no-cache -t app:latest', pct: 74 },
        { log: 'Build successful (12 stages, 38s)', pct: 86 },
        { log: 'Verifier: confirming image exists & runs', pct: 94 },
        { log: '✓ Docker image rebuilt: app:latest (428MB)', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Rebuild my Docker image' },
        { role: 'agent', text: 'Checking Docker environment... Daemon is running with Docker v24.0.7.' },
        { role: 'agent', text: 'Found Dockerfile with 12 stages. I\'ll do a clean rebuild with --no-cache.' },
        { role: 'agent', text: 'Auditor reviewed the Dockerfile — no security concerns.' },
        { role: 'agent', text: '✓ Build complete in 38s. Image: app:latest (428MB). Container starts successfully.' },
      ]
    },
    {
      label: 'Pull Stripe payouts',
      steps: [
        { log: 'Verifying Stripe API key...', pct: 7 },
        { log: 'Stripe API connected (mode: live)', pct: 17 },
        { log: 'Plan: query payouts, format as table', pct: 27 },
        { log: 'Tool selected: StripeTool', pct: 36 },
        { log: 'Writing Python Stripe script...', pct: 46 },
        { log: 'Auditor: reviewing financial data access', pct: 56 },
        { log: 'Auditor: ALLOW — read-only payouts', pct: 64 },
        { log: 'Executing: python fetch_payouts.py', pct: 76 },
        { log: 'Fetched 24 payouts ($48,230 total)', pct: 86 },
        { log: 'Verifier: reconciling payout totals', pct: 94 },
        { log: '✓ Payout report saved: stripe_payouts_2024.csv', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Get my Stripe payout history' },
        { role: 'agent', text: 'Connecting to Stripe API... Authenticated successfully.' },
        { role: 'agent', text: 'I\'ll fetch all payouts from the last 90 days and format them into a clean report.' },
        { role: 'agent', text: 'Auditor confirmed read-only access to payouts endpoint.' },
        { role: 'agent', text: '✓ 24 payouts totaling $48,230 saved to stripe_payouts_2024.csv.' },
      ]
    },
    {
      label: 'Log a Notion entry',
      steps: [
        { log: 'Authenticating with Notion API...', pct: 7 },
        { log: 'Notion integration connected', pct: 16 },
        { log: 'Plan: create page in Tasks database', pct: 26 },
        { log: 'Tool selected: NotionAdvancedTool', pct: 35 },
        { log: 'Writing Python Notion script...', pct: 46 },
        { log: 'Auditor: reviewing database write scope', pct: 56 },
        { log: 'Auditor: ALLOW — single page creation', pct: 64 },
        { log: 'Executing: python notion_entry.py', pct: 74 },
        { log: 'Page created in Tasks database', pct: 86 },
        { log: 'Verifier: confirming page exists via API', pct: 94 },
        { log: '✓ Notion entry added to Tasks database.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Add a task to Notion' },
        { role: 'agent', text: 'Connecting to Notion via API... Integration is active.' },
        { role: 'agent', text: 'I\'ll create a new page in your Tasks database with title, status, and priority.' },
        { role: 'agent', text: 'Auditor approved the write operation. Creating the entry now...' },
        { role: 'agent', text: '✓ New task "Q4 Review" added to Notion Tasks database.' },
      ]
    },
    {
      label: 'Compress a video',
      steps: [
        { log: 'Scanning for video files...', pct: 6 },
        { log: 'Found: demo_recording.mp4 (1.2GB)', pct: 16 },
        { log: 'Plan: compress with H.264, target 100MB', pct: 26 },
        { log: 'Tool selected: FFmpegTool', pct: 34 },
        { log: 'Writing FFmpeg command...', pct: 44 },
        { log: 'Auditor: reviewing file modification safety', pct: 54 },
        { log: 'Auditor: ALLOW — creates new compressed file', pct: 62 },
        { log: 'Executing: ffmpeg -i demo_recording.mp4 ...', pct: 74 },
        { log: 'Compressed: 1.2GB → 86MB (93% reduction)', pct: 86 },
        { log: 'Verifier: checking output quality & size', pct: 94 },
        { log: '✓ Video compressed: demo_recording_compressed.mp4 (86MB)', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Compress my video file' },
        { role: 'agent', text: 'Searching for large video files in your workspace... Found demo_recording.mp4 at 1.2GB.' },
        { role: 'agent', text: 'I\'ll use H.264 encoding with CRF 23 to balance quality and size.' },
        { role: 'agent', text: 'Auditor confirmed the operation creates a new file — original is untouched.' },
        { role: 'agent', text: '✓ Compressed from 1.2GB to 86MB with excellent quality retention!' },
      ]
    },
    {
      label: 'Batch-resize photos',
      steps: [
        { log: 'Scanning Pictures folder...', pct: 6 },
        { log: 'Found 48 images (JPEG, PNG)', pct: 16 },
        { log: 'Plan: resize to 1920px wide, maintain aspect', pct: 26 },
        { log: 'Tool selected: ImageAdvancedTool', pct: 34 },
        { log: 'Writing Python Pillow script...', pct: 44 },
        { log: 'Auditor: reviewing for data safety', pct: 54 },
        { log: 'Auditor: ALLOW — creates resized copies', pct: 62 },
        { log: 'Executing: python batch_resize.py', pct: 74 },
        { log: 'Resized 48/48 images in 2.3s', pct: 86 },
        { log: 'Verifier: checking output dimensions', pct: 94 },
        { log: '✓ 48 photos resized to 1920px wide.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Resize all my photos' },
        { role: 'agent', text: 'Scanning Pictures folder for images... Found 48 photos.' },
        { role: 'agent', text: 'I\'ll resize all to 1920px wide, preserving aspect ratio and EXIF data.' },
        { role: 'agent', text: 'Auditor approved — creates copies, originals remain untouched.' },
        { role: 'agent', text: '✓ 48 photos resized in 2.3 seconds. Sharp and clean.' },
      ]
    },
    {
      label: 'Deploy via SSH',
      steps: [
        { log: 'Checking SSH configuration...', pct: 6 },
        { log: 'SSH key loaded: ed25519', pct: 16 },
        { log: 'Plan: rsync files, restart service', pct: 26 },
        { log: 'Tool selected: TerminalTool, SSH utils', pct: 34 },
        { log: 'Writing deployment script...', pct: 44 },
        { log: 'Auditor: reviewing SSH + command safety', pct: 54 },
        { log: 'Auditor: ALLOW — known host, standard deploy', pct: 64 },
        { log: 'Executing: rsync -avz ./dist/ server:/app/', pct: 76 },
        { log: 'Deployed: 124 files, 0 conflicts', pct: 86 },
        { log: 'Verifier: confirming service is running', pct: 94 },
        { log: '✓ Deployment complete. Service restarted.', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Deploy my app to server' },
        { role: 'agent', text: 'Checking SSH connection to production server... Connected via ed25519 key.' },
        { role: 'agent', text: 'I\'ll rsync the dist folder and restart the service with zero downtime.' },
        { role: 'agent', text: 'Auditor approved the deployment script — safe commands only.' },
        { role: 'agent', text: '✓ 124 files deployed. Service restarted successfully.' },
      ]
    },
    {
      label: 'Transcribe voice memo',
      steps: [
        { log: 'Scanning for audio files...', pct: 6 },
        { log: 'Found: meeting_notes.m4a (14min)', pct: 16 },
        { log: 'Plan: transcribe with speaker diarization', pct: 26 },
        { log: 'Tool selected: SpeechAITool', pct: 34 },
        { log: 'Writing Python transcription script...', pct: 44 },
        { log: 'Auditor: reviewing audio processing safety', pct: 54 },
        { log: 'Auditor: ALLOW — local processing', pct: 62 },
        { log: 'Executing: python transcribe.py', pct: 74 },
        { log: 'Transcribed: 14min audio → 2,400 words', pct: 86 },
        { log: 'Verifier: checking transcript accuracy', pct: 94 },
        { log: '✓ Transcript saved: meeting_notes_transcript.txt', pct: 100 },
      ],
      messages: [
        { role: 'user', text: 'Transcribe this voice memo' },
        { role: 'agent', text: 'Found meeting_notes.m4a — 14 minutes. I\'ll use Whisper for transcription with speaker labels.' },
        { role: 'agent', text: 'Audio is clear. Processing locally for privacy.' },
        { role: 'agent', text: 'Auditor confirmed local-only processing. No data leaves your machine.' },
        { role: 'agent', text: '✓ 2,400 words transcribed with 3 speaker labels. Saved as text file.' },
      ]
    },
  ],
  currentTask: null,
  running: false,
  timeoutId: null,
};

function selectChip(index, btn) {
  document.querySelectorAll('.tool-chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  demoData.currentTask = index;
  document.getElementById('demo-input').value = demoData.tasks[index].label;
}

function runDemo() {
  if (demoData.running) return;
  const index = demoData.currentTask;
  if (index === null || index === undefined) {
    const chips = document.querySelectorAll('.tool-chip');
    if (chips.length > 0) {
      chips[0].classList.add('active');
      demoData.currentTask = 0;
      document.getElementById('demo-input').value = demoData.tasks[0].label;
    }
  }

  const taskIndex = demoData.currentTask;
  if (taskIndex === null || taskIndex === undefined) return;

  const task = demoData.tasks[taskIndex];
  demoData.running = true;

  document.getElementById('demo-run-btn').disabled = true;
  document.getElementById('demo-run-btn').textContent = '■ Running...';

  const chat = document.getElementById('demo-chat');
  const log = document.getElementById('demo-log');
  const prog = document.getElementById('demo-prog');
  const pct = document.getElementById('demo-pct');
  const status = document.getElementById('demo-status');

  chat.innerHTML = '';
  log.innerHTML = '<div class="app-log-header">Execution Logs</div>';
  prog.style.width = '0%';
  pct.textContent = '0%';
  status.textContent = 'Starting...';

  let msgIdx = 0;
  let stepIdx = 0;

  function addLog(text) {
    const line = document.createElement('div');
    line.className = 'app-log-line';
    line.textContent = `> ${text}`;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
  }

  function addMessage(role, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    bubble.innerHTML = `<div class="chat-bubble-text">${text}</div>`;
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
  }

  function showThinking() {
    const div = document.createElement('div');
    div.className = 'chat-thinking';
    div.id = 'thinking-el';
    div.innerHTML = '<div class="chat-thinking-dot"></div><div class="chat-thinking-dot"></div><div class="chat-thinking-dot"></div>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function hideThinking() {
    const el = document.getElementById('thinking-el');
    if (el) el.remove();
  }

  addMessage('user', task.messages[0].text);
  msgIdx = 1;
  showThinking();

  function nextStep() {
    if (stepIdx >= task.steps.length) {
      status.textContent = 'Complete';
      demoData.running = false;
  document.getElementById('demo-run-btn').disabled = false;
  document.getElementById('demo-run-btn').innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run';
  return;
}

    const step = task.steps[stepIdx];
    addLog(step.log);
    prog.style.width = step.pct + '%';
    pct.textContent = step.pct + '%';
    status.textContent = step.log.substring(0, 45) + (step.log.length > 45 ? '...' : '');

    const milestones = [25, 50, 75, 100];
    while (msgIdx < task.messages.length) {
      const nextMs = milestones[msgIdx - 1];
      if (nextMs !== undefined && step.pct >= nextMs) {
        if (step.pct >= 100) hideThinking();
        addMessage('agent', task.messages[msgIdx].text);
        msgIdx++;
      } else {
        break;
      }
    }

    stepIdx++;

    const delay = step.pct >= 100 ? 1200 : (step.pct > 80 ? 900 : 600);
    demoData.timeoutId = setTimeout(nextStep, delay);
  }

  setTimeout(nextStep, 800);
}

function killDemo() {
  if (demoData.timeoutId) {
    clearTimeout(demoData.timeoutId);
    demoData.timeoutId = null;
  }
  demoData.running = false;
  hideThinking();
  document.getElementById('demo-run-btn').disabled = false;
  document.getElementById('demo-run-btn').innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run';
  document.getElementById('demo-status').textContent = 'Killed';
  const log = document.getElementById('demo-log');
  const line = document.createElement('div');
  line.className = 'app-log-line';
  line.textContent = '! Execution terminated by user';
  line.style.color = 'var(--rose)';
  log.appendChild(line);
}

// ── Mobile menu ──
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.querySelector('.mobile-menu-btn');
  const links = document.querySelector('.nav-links');
  if (btn && links) {
    btn.addEventListener('click', () => {
      const isOpen = links.style.display === 'flex';
      links.style.display = isOpen ? '' : 'flex';
      if (!isOpen) {
        links.style.flexDirection = 'column';
        links.style.position = 'fixed';
        links.style.top = '64px';
        links.style.left = '0';
        links.style.right = '0';
        links.style.background = 'var(--nav-bg)';
        links.style.backdropFilter = 'blur(20px)';
        links.style.padding = '20px 24px';
        links.style.borderBottom = '1px solid var(--border)';
        links.style.gap = '20px';
      }
    });
  }
});

// ── Input enter key ──
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('demo-input');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') runDemo();
    });
  }
});
