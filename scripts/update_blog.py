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
    """글이 실제로 벨로그에 올라간 시각(KST)을 ISO 8601 문자열로 반환.
    Actions 실행 시각이 아니라 이 시각을 커밋 날짜로 써야, 늦게 감지되더라도
    GitHub 잔디에 실제로 글을 쓴 날짜로 반영된다."""
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

        # 깃허브 커밋 (실제 발행 시각을 커밋 날짜로 사용)
        repo.git.add(file_path)
        commit_message = f'Add post: {entry.title}' if is_new else f'Update post: {entry.title}'
        commit_date = get_published_kst(entry)
        if commit_date:
            with repo.git.custom_environment(GIT_AUTHOR_DATE=commit_date, GIT_COMMITTER_DATE=commit_date):
                repo.git.commit('-m', commit_message)
        else:
            repo.git.commit('-m', commit_message)

# 변경 사항을 깃허브에 푸시
repo.git.push()
