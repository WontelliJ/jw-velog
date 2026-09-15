<p>연합동아리 스터디를 계기로 velog를 시작합니다.</p>
<h2 id="이-블로그의-역할">이 블로그의 역할</h2>
<ul>
<li>공부한 내용 정리</li>
<li>에러 해결 과정 기록</li>
</ul>
<h2 id="무엇을-적을까">무엇을 적을까</h2>
<h3 id="til-today-i-learned">TIL (Today I Learned)</h3>
<p>오늘 배운 Java 문법, 스프링 개념 등을 가볍게 정리합니다.</p>
<h3 id="🔥-트러블슈팅-가장-중요">🔥 트러블슈팅 (가장 중요)</h3>
<p>프로젝트를 하다가 A라는 에러가 났는데, B인 줄 알았더니 C가 원인이었고, D로 해결했다 — 이런 흐름으로 기록합니다.</p>
<h2 id="참고-자료">참고 자료</h2>
<ul>
<li><a href="https://velog.io/@yuuuye/velog-%EB%A7%88%ED%81%AC%EB%8B%A4%EC%9A%B4MarkDown-%EC%9E%91%EC%84%B1%EB%B2%95">velog 마크다운 작성법</a></li>
<li><a href="https://velog.io/@ju_hyanghyang/GitHub-GitHub%EC%99%80-Velog-%EC%97%B0%EB%8F%99%ED%95%98%EA%B8%B0">GitHub · Velog 연동하기</a></li>
</ul>
<h2 id="github-연동-보완">GitHub 연동, 보완</h2>
<p>위 글의 절차를 따라간 뒤, 아래 세 가지를 추가로 반영하면 커밋 자동화 + 잔디 반영 + 수정 글 반영까지 됩니다. (적용 후 실제로 잔디에 반영되는지는 확인해서 업데이트 예정)</p>
<h3 id="1-yml의-하드코딩된-push-스텝-제거">1. yml의 하드코딩된 push 스텝 제거</h3>
<p>글에 있는 아래 스텝은 지우는 게 맞습니다.</p>
<p>```yaml</p>
<ul>
<li>name: Push changes
run: |
  git config --global user.name 'github-actions[bot]'
  git config --global user.email 'github-actions[bot]@users.noreply.github.com'
  git push https://${{ secrets.GH_PAT }}@github.com/[2.깃허브아이디]/velog.git
```</li>
</ul>
<p>실제 커밋/푸시는 파이썬 스크립트의 GitPython이 처리하기 때문에 이 스텝 자체가 불필요하고, 리포 이름을 <code>velog.git</code>으로 고정해놔서 실제 리포 이름이 다르면(예: <code>jw-velog</code>) &quot;Repository not found&quot;가 납니다.</p>
<h3 id="2-잔디-반영을-위한-커밋-작성자-설정">2. 잔디 반영을 위한 커밋 작성자 설정</h3>
<p>커밋 author 이메일이 본인 GitHub 계정에 연결된 이메일이어야 잔디에 카운트됩니다. <code>github-actions[bot]</code> 명의로 커밋하면 레포에는 쌓이지만 잔디엔 안 잡힙니다.</p>
<h3 id="3-글-수정-시-반영되도록-스크립트-수정">3. 글 수정 시 반영되도록 스크립트 수정</h3>
<p>원본 스크립트는 <code>if not os.path.exists(file_path):</code>로 파일이 이미 있으면 무조건 건너뛰기 때문에, velog에서 기존 글을 고쳐도 반영이 안 됩니다.</p>
<h3 id="최종본">최종본</h3>
<p>위 세 가지를 모두 반영한 최종 코드입니다. 이걸로 통째로 교체하면 됩니다.</p>
<p><strong><code>.github/workflows/update_blog.yml</code></strong> (레포 루트의 <code>.github/workflows/</code> 아래)</p>
<p>```yaml
name: Update Blog Posts</p>
<p>on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 15 * * *'   # UTC 15:00 = 한국 시간 매일 자정
  workflow_dispatch:</p>
<p>jobs:
  update_blog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GH_PAT }}</p>
<pre><code>  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.x'

  - name: Install dependencies
    run: pip install feedparser gitpython

  - name: Configure git
    run: |
      git config --global user.name '본인_깃허브_아이디'
      git config --global user.email '본인_깃허브_noreply_또는_인증된_이메일'

  - name: Run script
    run: python scripts/update_blog.py</code></pre><p>```</p>
<p><strong><code>scripts/update_blog.py</code></strong> (반드시 레포 루트 기준 <code>scripts/</code> 폴더)</p>
<p>```python
import feedparser
import git
import os</p>
<p>rss_url = '<a href="https://api.velog.io/rss/@%EB%B3%B8%EC%9D%B8%EB%B2%A8%EB%A1%9C%EA%B7%B8%EC%95%84%EC%9D%B4%EB%94%94'">https://api.velog.io/rss/@본인벨로그아이디'</a>
repo_path = '.'
posts_dir = os.path.join(repo_path, 'velog-posts')</p>
<p>if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)</p>
<p>repo = git.Repo(repo_path)
feed = feedparser.parse(rss_url)</p>
<p>changed = False
for entry in feed.entries:
    file_name = entry.title.replace('/', '-').replace('\\', '-') + '.md'
    file_path = os.path.join(posts_dir, file_name)
    new_content = entry.description</p>
<pre><code>if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        old_content = f.read()
    if old_content == new_content:
        continue
    commit_msg = f'Update post: {entry.title}'
else:
    commit_msg = f'Add post: {entry.title}'

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

repo.git.add(file_path)
repo.git.commit('-m', commit_msg)
changed = True</code></pre><p>if changed:
    repo.git.push()
```</p>
<p>이메일은 실제 이메일을 노출하기 싫으면 GitHub Settings → Emails에서 <strong>Keep my email addresses private</strong>를 켜면 나오는 <code>숫자+아이디@users.noreply.github.com</code> 형태의 주소를 쓰면 됩니다.</p>
<p>레포가 private라면 GitHub 프로필 설정 → Contributions &amp; Activity에서 <strong>Include private contributions on my profile</strong>을 켜야 잔디에 반영됩니다.</p>