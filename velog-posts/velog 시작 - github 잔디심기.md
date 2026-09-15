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
<p>위 글의 절차를 따라간 뒤, 아래 다섯 가지를 추가로 반영하면 커밋 자동화 + 잔디 반영 + 수정 글 반영까지 됩니다. (실제로 다 적용해서 잔디에 반영되는 것까지 확인했습니다.)</p>
<h3 id="1-yml의-하드코딩된-push-스텝-제거">1. yml의 하드코딩된 push 스텝 제거</h3>
<p>글에 있는 아래 스텝은 지우는 게 맞습니다.</p>
<pre><code class="language-yaml">- name: Push changes
  run: |
    git config --global user.name 'github-actions[bot]'
    git config --global user.email 'github-actions[bot]@users.noreply.github.com'
    git push https://${{ secrets.GH_PAT }}@github.com/[2.깃허브아이디]/velog.git</code></pre>
<p>실제 커밋/푸시는 파이썬 스크립트의 GitPython이 처리하기 때문에 이 스텝 자체가 불필요하고, 리포 이름을 <code>velog.git</code>으로 고정해놔서 실제 리포 이름이 다르면(예: <code>jw-velog</code>) Repository not found가 납니다.</p>
<h3 id="2-잔디-반영을-위한-커밋-작성자-설정">2. 잔디 반영을 위한 커밋 작성자 설정</h3>
<p>커밋 author 이메일이 본인 GitHub 계정에 연결된 이메일이어야 잔디에 카운트됩니다. <code>github-actions[bot]</code> 명의로 커밋하면 레포에는 쌓이지만 잔디엔 안 잡힙니다.</p>
<h3 id="3-글-수정-시-반영되도록-스크립트-수정">3. 글 수정 시 반영되도록 스크립트 수정</h3>
<p>원본 스크립트는 <code>if not os.path.exists(file_path):</code>로 파일이 이미 있으면 무조건 건너뛰기 때문에, velog에서 기존 글을 고쳐도 반영이 안 됩니다.</p>
<h3 id="4-벨로그-pubdate가-수정해도-안-바뀌는-문제">4. 벨로그 pubDate가 수정해도 안 바뀌는 문제</h3>
<p>GitHub 잔디는 <strong>Actions가 실행된 시각이 아니라 커밋에 박힌 author date</strong>를 기준으로 날짜가 정해집니다. 그래서 자정 직전에 글을 올렸는데 봇이 다음 날 새벽에야 감지하면, 커밋 시각이 다음 날이 되어 하루 밀려서 잔디에 찍힙니다.</p>
<p>이걸 막으려면 새 글일 때는 RSS의 실제 발행 시각(<code>entry.published</code>)을 커밋 날짜로 강제 지정하면 됩니다. 다만 <strong>주의할 점</strong>: 벨로그의 <code>pubDate</code>는 글을 수정해도 최초 발행 시각 그대로 고정되고 갱신되지 않습니다. 그래서 이 로직을 글 수정 케이스에도 똑같이 적용하면, 수정한 오늘 날짜가 아니라 엉뚱하게 원래 처음 발행했던 날짜로 커밋이 찍혀버립니다. <strong>새 글일 때만 발행 시각을 쓰고, 기존 글을 수정한 경우엔 감지된(=지금) 시각을 그대로 써야</strong> 합니다.</p>
<p>(참고로 제목을 통째로 바꾸면 파일명이 바뀌어서 스크립트가 새 글로 착각합니다 — 즉 제목까지 바꾸는 수정은 이 pubDate 문제를 다시 겪을 수 있으니, 제목은 웬만하면 유지하는 걸 추천합니다.)</p>
<h3 id="5-파일명에-windows-금지-문자가-들어가면-로컬-클론이-깨지는-문제">5. 파일명에 Windows 금지 문자가 들어가면 로컬 클론이 깨지는 문제</h3>
<p>원본 스크립트는 파일명에서 <code>/</code>, <code>\</code> 만 걸러냅니다. 그런데 글 제목에 <code>?</code>, <code>:</code>, <code>*</code>, <code>&quot;</code>, <code>&lt;</code>, <code>&gt;</code>, <code>|</code> 같은 문자가 들어가면 어떻게 될까요? GitHub Actions는 리눅스 러너라 커밋 자체는 문제없이 되지만, <strong>Windows에서 그 저장소를 <code>git clone</code>/<code>git pull</code> 하는 순간 invalid path 에러로 통째로 실패</strong>합니다. 정규식으로 Windows 금지 문자를 전부 걸러내야 크로스플랫폼으로 안전합니다.</p>
<h3 id="최종본">최종본</h3>
<p>위 다섯 가지를 모두 반영한 최종 코드입니다. 이걸로 통째로 교체하면 됩니다.</p>
<p><strong><code>.github/workflows/update_blog.yml</code></strong> (레포 루트의 <code>.github/workflows/</code> 아래)</p>
<pre><code class="language-yaml">name: Update Blog Posts

on:
  push:
    branches:
      - main # 또는 워크플로우를 트리거하고 싶은 브랜치 이름
  schedule:
    - cron: '0 0 * * *'  # 매일 UTC 00:00 = 한국 시간 오전 9시
    - cron: '0 15 * * *' # 매일 UTC 15:00 = 한국 시간 자정(00:00)
  workflow_dispatch: # Actions 탭에서 수동으로 즉시 실행하고 싶을 때

jobs:
  update_blog:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Set up Git identity
      run: |
        git config --global user.name '본인_깃허브_아이디'
        git config --global user.email '본인_깃허브_noreply_또는_인증된_이메일'
        git remote set-url origin https://${{ secrets.GH_PAT }}@github.com/[본인깃허브아이디]/[레포이름].git

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install feedparser gitpython

    - name: Run script
      run: python scripts/update_blog.py</code></pre>
<p><strong><code>scripts/update_blog.py</code></strong> (반드시 레포 루트 기준 <code>scripts/</code> 폴더)</p>
<pre><code class="language-python">import calendar
import feedparser
import git
import os
import re
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

rss_url = 'https://api.velog.io/rss/@본인벨로그아이디'
repo_path = '.'
posts_dir = os.path.join(repo_path, 'velog-posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

repo = git.Repo(repo_path)
feed = feedparser.parse(rss_url)


def get_published_kst(entry):
    &quot;&quot;&quot;글이 처음 벨로그에 올라간 시각(KST)을 ISO 8601 문자열로 반환.
    새 글을 늦게 감지하더라도(예: 자정 직전 발행) 실제 발행 시각 기준으로
    GitHub 잔디에 반영되게 하기 위함. 벨로그 RSS의 pubDate는 글을 수정해도
    갱신되지 않고 최초 발행 시각으로 고정되므로, 기존 글 수정 시에는 이 값을
    쓰지 않고 감지된(=지금) 시각을 그대로 커밋 날짜로 사용해야 한다.&quot;&quot;&quot;
    struct_time = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
    if not struct_time:
        return None
    utc_dt = datetime.fromtimestamp(calendar.timegm(struct_time), tz=timezone.utc)
    return utc_dt.astimezone(KST).isoformat()


for entry in feed.entries:
    # Windows 파일명 금지 문자 \ / : * ? &quot; &lt; &gt; | 를 전부 제거
    file_name = re.sub(r'[\\/:*?&quot;&lt;&gt;|]', '', entry.title).strip()
    file_name += '.md'
    file_path = os.path.join(posts_dir, file_name)

    is_new = not os.path.exists(file_path)

    existing_content = None
    if not is_new:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

    if is_new or existing_content != entry.description:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(entry.description)

        repo.git.add(file_path)
        commit_message = f'Add post: {entry.title}' if is_new else f'Update post: {entry.title}'
        # 새 글이면 실제 발행 시각으로, 기존 글 수정이면 지금 감지한 시각 그대로 커밋한다.
        commit_date = get_published_kst(entry) if is_new else None
        if commit_date:
            with repo.git.custom_environment(GIT_AUTHOR_DATE=commit_date, GIT_COMMITTER_DATE=commit_date):
                repo.git.commit('-m', commit_message)
        else:
            repo.git.commit('-m', commit_message)

repo.git.push()</code></pre>
<p>이메일은 실제 이메일을 노출하기 싫으면 GitHub Settings → Emails에서 <strong>Keep my email addresses private</strong>를 켜면 나오는 <code>숫자+아이디@users.noreply.github.com</code> 형태의 주소를 쓰면 됩니다.</p>
<p>레포가 private라면 GitHub 프로필 설정 → Contributions &amp; Activity에서 <strong>Include private contributions on my profile</strong>을 켜야 잔디에 반영됩니다.</p>