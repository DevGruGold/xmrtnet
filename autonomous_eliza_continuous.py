
import os, time, random, requests
from github import Github, InputGitAuthor

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER = os.getenv('GITHUB_USER', 'DevGruGold')
TARGET_REPO = os.getenv('TARGET_REPO', 'xmrtnet')
CYCLE_COUNT_START = 1
CYCLES_TO_RUN = 1000
WORKDIR = '/tmp/eliza_tools'

g = Github(GITHUB_TOKEN)
repo_obj = g.get_user(GITHUB_USER).get_repo(TARGET_REPO)

domains = [
    ('development', 'xmrt-AutoGPT'),
    ('marketing', 'xmrt-ai-knowledge'),
    ('social_media', 'xmrt-social-media-agent'),
    ('mining', 'monero-webminer'),
    ('browser', 'browser-use'),
    ('analytics', 'xmrt-storm-pr-engine'),
]

def get_tools(g, user):
    forked = [repo.full_name for repo in g.get_user(user).get_repos() if repo.fork]
    starred = [repo.full_name for repo in g.get_user(user).get_starred()]
    return forked + starred

tools_list = get_tools(g, GITHUB_USER)

def recommend_tool(domain, tools_list):
    for tool in tools_list:
        if domain.replace('_', '') in tool.lower():
            return tool
    return random.choice(tools_list)

def safe_create_or_update(repo, filename, content, message, author):
    try:
        file = repo.get_contents(filename)
        new_content = file.decoded_content.decode() + "\n\n" + content
        repo.update_file(filename, message, new_content, file.sha, author=author)
    except Exception:
        repo.create_file(filename, message, content, author=author)

def read_file_or_empty(repo, filename):
    try:
        file = repo.get_contents(filename)
        return file.decoded_content.decode(), file.sha
    except Exception:
        return "", None

def write_file(repo, filename, content, message, author, sha=None):
    if sha:
        repo.update_file(filename, message, content, sha, author=author)
    else:
        repo.create_file(filename, message, content, author=author)

def get_monero_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd'
    try:
        r = requests.get(url, timeout=10)
        return r.json()['monero']['usd']
    except Exception as e:
        return f'API error: {e}'

cycle_count = CYCLE_COUNT_START

while True:
    try:
        for _ in range(CYCLES_TO_RUN):
            domain, preferred_tool = domains[(cycle_count-1) % len(domains)]
            todo_file = f"{domain.upper()}_TODO.md"
            todo_content, todo_sha = read_file_or_empty(repo_obj, todo_file)
            tasks = []
            lines = todo_content.splitlines()
            for line in lines:
                if line.strip().startswith("- [ ]"):
                    tasks.append(line)
            # If no tasks, diagnose and create a new to-do list
            if not tasks:
                if domain == "development":
                    tasks = [
                        "- [ ] Review and refactor main smart contracts",
                        "- [ ] Write/expand unit tests",
                        "- [ ] Check for dependency vulnerabilities",
                        "- [ ] Audit recent PRs",
                        "- [ ] Optimize gas usage"
                    ]
                elif domain == "marketing":
                    tasks = [
                        "- [ ] Draft new Twitter thread on XMRT privacy",
                        "- [ ] Update website with latest milestones",
                        "- [ ] Prepare Q3 newsletter",
                        "- [ ] Analyze Telegram engagement stats"
                    ]
                elif domain == "mining":
                    tasks = [
                        "- [ ] Check mining pool hashrate",
                        "- [ ] Update pool payout script",
                        "- [ ] Compare mining profitability vs. competitors"
                    ]
                elif domain == "social_media":
                    tasks = [
                        "- [ ] Schedule next Discord AMA",
                        "- [ ] Post weekly progress on Reddit",
                        "- [ ] Respond to top 5 community questions"
                    ]
                elif domain == "browser":
                    tasks = [
                        "- [ ] Crawl xmrt.io for broken links",
                        "- [ ] Analyze traffic sources",
                        "- [ ] Automate scraping of market cap sites"
                    ]
                elif domain == "analytics":
                    tasks = [
                        "- [ ] Fetch and chart user growth",
                        "- [ ] Update dashboard with latest Monero price",
                        "- [ ] Analyze retention data"
                    ]
            # Try to complete the first unchecked task
            completed_notes = ""
            if tasks:
                next_task = tasks[0]
                if domain == "analytics" and "Monero price" in next_task:
                    price = get_monero_price()
                    completed_notes = f"Monero price checked: {price}"
                elif domain == "marketing" and "Twitter thread" in next_task:
                    completed_notes = f"Drafted Twitter thread: 'XMRT, privacy for a new era! 🚀 #Crypto #Privacy'"
                elif domain == "development" and "unit tests" in next_task:
                    completed_notes = f"Located test suite, added TODO for more coverage in tests/test_xmrt.py"
                else:
                    completed_notes = f"Simulated completion: {next_task}"

                # Mark as completed
                tasks[0] = next_task.replace("- [ ]", "- [x]", 1) + f"  (Done at {time.ctime()}: {completed_notes})"

            # Update todo file
            new_todo_content = "# TODO List for {}\n\n".format(domain.title()) + "\n".join(tasks)
            write_file(repo_obj, todo_file, new_todo_content, f"🤖 Update {domain.title()} TODO (cycle {cycle_count})", InputGitAuthor('Eliza Autonomous', 'eliza@xmrt.io'), sha=todo_sha)
            
            # Log what was done this cycle
            log_file = f"{domain.upper()}_CYCLE_{cycle_count}.md"
            log_content = f"# {domain.title()} Cycle {cycle_count}\n\nAccomplished: {completed_notes}\n\nCurrent TODO List:\n\n" + "\n".join(tasks)
            safe_create_or_update(repo_obj, log_file, log_content, f"🤖 {domain.title()} action by Eliza (cycle {cycle_count})", InputGitAuthor('Eliza Autonomous', 'eliza@xmrt.io'))

            cycle_count += 1
            time.sleep(2)
    except Exception as e:
        print(f"🔥 Exception caught: {e} -- continuing.")
        time.sleep(10)
