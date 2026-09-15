import calendar
import feedparser
import git
import os
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

# 벨로그 RSS 피드 URL
# example : rss_url = 'https://api.velog.io/rss/@rimgosu'
rss_url = 'https://api.velog.io/rss/@wontellij'

# 깃허브 레포지토리 경로
repo_path = '.'

# 'velog-posts' 폴더 경로
posts_dir = os.path.join(repo_path, 'velog-posts')

# 'velog-posts' 폴더가 없다면 생성
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

# 레포지토리 로드
repo = git.Repo(repo_path)

# RSS 피드 파싱
feed = feedparser.parse(rss_url)


def get_published_kst(entry):
    """글이 처음 벨로그에 올라간 시각(KST)을 ISO 8601 문자열로 반환.
    새 글을 늦게 감지하더라도(예: 자정 직전 발행) 실제 발행 시각 기준으로
    GitHub 잔디에 반영되게 하기 위함. 벨로그 RSS의 pubDate는 글을 수정해도
    갱신되지 않고 최초 발행 시각으로 고정되므로, 기존 글 수정 시에는 이 값을
    쓰지 않고 감지된(=지금) 시각을 그대로 커밋 날짜로 사용해야 한다."""
    struct_time = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
    if not struct_time:
        return None
    utc_dt = datetime.fromtimestamp(calendar.timegm(struct_time), tz=timezone.utc)
    return utc_dt.astimezone(KST).isoformat()

# 각 글을 파일로 저장하고 커밋
for entry in feed.entries:
    # 파일 이름에서 유효하지 않은 문자 제거 또는 대체
    file_name = entry.title
    file_name = file_name.replace('/', '-')  # 슬래시를 대시로 대체
    file_name = file_name.replace('\\', '-')  # 백슬래시를 대시로 대체
    # 필요에 따라 추가 문자 대체
    file_name += '.md'
    file_path = os.path.join(posts_dir, file_name)

    # 새 글이면 생성, 이미 있는 글이면 내용이 바뀐 경우에만 갱신
    is_new = not os.path.exists(file_path)

    existing_content = None
    if not is_new:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

    if is_new or existing_content != entry.description:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(entry.description)  # 글 내용을 파일에 작성

        # 깃허브 커밋
        repo.git.add(file_path)
        # 새 글이면 실제 발행 시각으로, 기존 글 수정이면 지금 감지한 시각 그대로 커밋한다.
        # (벨로그 RSS의 pubDate는 수정해도 최초 발행 시각에서 안 바뀌기 때문에,
        #  수정 글에 pubDate를 쓰면 오히려 엉뚱한 날짜로 잔디가 찍힌다.)
        commit_message = f'Add post: {entry.title}' if is_new else f'Update post: {entry.title}'
        commit_date = get_published_kst(entry) if is_new else None
        if commit_date:
            with repo.git.custom_environment(GIT_AUTHOR_DATE=commit_date, GIT_COMMITTER_DATE=commit_date):
                repo.git.commit('-m', commit_message)
        else:
            repo.git.commit('-m', commit_message)

# 변경 사항을 깃허브에 푸시
repo.git.push()
