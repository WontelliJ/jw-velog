# LLM은 어떻게 답을 만드나: 구조, Transformer, 실제 모델로 확인한 결과

LLM이 문장을 받아 다음 단어 하나를 고르기까지의 과정을 하나의 예시 문장으로 따라간다. 개념 설명에서 그치지 않고 공개 모델 GPT-2와 Qwen2.5에 같은 문장을 넣어 중간값을 직접 꺼내 보았다. 실습의 숫자는 모두 코드를 실제로 실행한 결과이다.

---

## 0. 왜 Attention인가

본문에 앞서 세 가지를 짚고 넘어간다. 이 글에서 다루는 내용이 LLM(Large Language Model, 대규모 언어 모델. 많은 글을 학습해서 다음에 올 말을 예측하는 모델) 역사에서 어디쯤에 있는지, Attention이라는 말이 원래 무슨 뜻인지, 그리고 이 방식이 왜 판을 바꿨는지이다. 뒤의 각 장도 첫머리에서 같은 순서로 짧게 다룬다.

### 0.1 역사에서 어디쯤인가

![그림 1](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-01.png)

노란 칸이 이 글에서 다루는 범위로, 2017년 Transformer(구글 연구진이 발표한 신경망 구조. 지금 LLM 대부분의 기반)부터 지금 쓰는 대화형 LLM까지이다. RNN(Recurrent Neural Network, 순환 신경망)은 단어를 하나씩 읽으며 기억을 다음 칸에 넘기는 신경망이고, LSTM(Long Short-Term Memory)은 그 기억을 더 오래 유지하도록 고친 RNN이다. Seq2Seq(Sequence to Sequence)는 문장을 읽는 부분과 만드는 부분을 이어 붙인 번역 구조이다. 그림의 GPT, BERT, ChatGPT, Llama, Qwen은 모두 Transformer를 바탕으로 만든 언어 모델 이름이다.

| 시기 | 컴퓨터가 글을 다룬 방식 | 한계 |
|---|---|---|
| 규칙 | 사람이 문법과 단어 사전을 직접 넣는다 | 예외가 끝이 없다 |
| 통계 | 어떤 단어 다음에 어떤 단어가 자주 오는지 센다 | 바로 앞 두세 단어만 본다 |
| RNN, LSTM | 신경망이 한 단어씩 읽으며 기억을 넘긴다 | 문장이 길면 앞 내용이 흐려진다. 차례로 읽어서 느리다 |
| Transformer | 모든 단어를 한꺼번에 놓고 서로 비교한다 | 단어끼리 모두 비교하므로 글이 길어지면 계산량이 길이의 제곱으로 늘어난다 |

### 0.2 Attention이라는 말

Attention은 영어로 '주의, 주목'이라는 뜻이며, 안내 방송의 Attention, please가 바로 이 말이다. 사람은 글을 읽을 때 모든 단어에 같은 힘을 쓰지 않고, 질문에 답하는 데 필요한 단어에 먼저 눈이 간다.

```text
민수는 사과를 좋아하고 지수는 포도를 좋아해. 민수 생일 선물로 뭘 살까?
```

예를 들어 위 문장에서 '살까'를 읽은 사람은 '민수'와 '사과'에 눈이 가고 '지수'와 '포도'는 덜 본다. Attention은 이 행동을 계산으로 옮긴 것이다. 즉, 단어마다 앞에 나온 단어 중 어디에 얼마나 주목할지 비율을 정하고, 그 비율만큼 정보를 가져온다.

### 0.3 왜 판이 바뀌었나

![그림 2](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-02.png)

RNN은 귓속말 전달 게임과 비슷하다. 앞사람에게 들은 말을 다음 사람에게 넘기는 방식이라 줄이 길면 처음 말이 흐려지고, 한 명씩 차례로 넘기니 느리기도 하다. 반면 Transformer는 모두가 한 방에 모여 필요한 사람에게 바로 묻는 방식에 가깝기 때문에 멀리 떨어진 단어도 한 번에 연결된다.

| | 예전 (RNN) | Transformer |
|---|---|---|
| 읽는 방식 | 한 단어씩 차례로 | 문장 전체를 한꺼번에 |
| 먼 단어 연결 | 여러 번 전달해야 해서 흐려진다 | 직접 연결한다 |
| 계산 속도 | 앞 단어가 끝나야 다음을 계산한다 | 동시에 계산해서 GPU로 빠르다 |
| 키우기 | 키워도 효과가 금방 막힌다 | 키울수록 성능이 계속 올랐다 |

> GPU: 같은 계산을 수천 개 동시에 하는 칩. 원래 게임 그래픽용으로 만들었다.

판을 바꾼 것은 표의 마지막 줄이다. 한꺼번에 계산할 수 있게 되면서 많은 글로 큰 모델을 학습할 수 있었고, 모델을 키울수록 성능이 좋아졌다. 그 결과가 GPT-3(2020년 OpenAI가 발표한 대형 언어 모델)와 ChatGPT(GPT-3 계열을 대화용으로 다듬어 2022년 공개한 서비스)이다. 논문 제목이 Attention Is All You Need(필요한 건 Attention뿐)인 것도 그때까지 보조 장치였던 Attention을 중심에 두고 RNN과 합성곱을 뺐기 때문이다. Block 안에는 Attention 말고도 FFN(5.3)이 함께 들어 있다.

이 글은 설명보다 직접 실행한 결과를 중심으로 정리했다. Attention이 실제로 앞 단어에 주목하는지는 실습 4-3과 실습 6에서, 모델이 실제로 '사과'라고 답하는지는 실습 4와 실습 7에서 확인한다.

---

## 이 글에서 다루는 범위

이 글은 GPT 같은 LLM이 문장을 받아 다음 Token(모델이 글을 처리하는 단위. 단어 하나일 수도 있고 글자 하나나 그보다 작은 조각일 수도 있다) 하나를 고르는 과정만 다룬다. Transformer 논문(Attention Is All You Need, 2017)은 문장을 읽는 Encoder와 문장을 만드는 Decoder 두 부분으로 되어 있는데, 이 중 GPT가 가져다 쓴 Decoder 쪽 구조만 본다.

![그림 3](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-03.png)

| 다룬다 | 짧게만 본다 | 다루지 않는다 |
|---|---|---|
| Decoder-Only 구조와 논문과의 차이, Block을 지나며 답이 생기는 과정, 학습, 실제 모델 실습 | 기본 단계의 실제 결과 (Tokenization, Attention 비율, Sampling) | 논문의 번역 구조와 수식, 학습 인프라, 사람 평가로 하는 추가 학습. 역사는 위치만 짚는다 |

> Decoder-Only: Decoder만 쓰는 구조.
>
> Block: Attention과 FFN을 묶은 계산 묶음으로, 모델은 이것을 여러 층 쌓는다.
>
> Tokenization: 문장을 Token으로 자르는 일.
>
> Sampling: 확률에 따라 다음 Token 하나를 뽑는 일.

구성은 1~4장 기본 단계, 5장 Decoder-Only, 6장 실습, 7장 학습 순이다. 설명을 위해 만든 숫자는 따로 표시했으며, 실습의 숫자는 모두 코드를 실제로 실행한 결과이다.

---

## 한눈에 보기 1. 전체 흐름

LLM이 하는 일은 지금까지의 글을 보고 다음 Token 하나를 고르는 것이며, 답이 끝날 때까지 이 일을 반복한다.

![그림 4](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-04.png)

| 부분 | 하는 일 | 예시에서 |
|---|---|---|
| ① 글을 숫자로 | 신경망이 계산할 수 있게 글자를 숫자 벡터로 바꾼다 | '민수', '사과'가 벡터가 된다 |
| ② 문맥 모으기 | 각 Token이 앞쪽 Token의 정보를 모으고 가공한다. 여러 번 반복한다 | 마지막 자리에 민수가 사과를 좋아한다는 정보가 모인다 |
| ③ 다음 Token 고르기 | 후보 전체에 확률을 매기고 하나를 고른다 | '사과'가 1위 |
| ④ 반복 | 고른 Token을 붙여 ①부터 다시 한다 | 사과 → 를 → 추천해요 |

> 벡터: 숫자 여러 개를 한 줄로 묶은 값. 예: [0.9, 0.8, 0.1].
>
> Embedding: Token 번호를 벡터로 바꾸는 표.
>
> Self-Attention: 같은 문장 안의 Token끼리 서로 주목해 정보를 가져오는 계산.

---

## 한눈에 보기 2. 전체 구조

같은 흐름을 실제 모델의 부품으로 그리면 아래와 같다. 그림은 GPT-2(124M) 기준이며, 실습 4에서 이 모델을 직접 실행한다. 124M은 가중치(신경망 안에서 곱해지는 숫자. 처음엔 무작위 값이고 학습으로 정해진다)가 1억 2,400만(124 Million) 개라는 뜻이다.

![그림 5](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-05.png)

| 부품 | 크기 (GPT-2) | 흐름에서 |
|---|---|---|
| Tokenizer 사전 | Token 50,257개 | ① |
| 벡터 한 개 | 숫자 768개 | ① |
| 한 번에 읽는 길이 | Token 1,024개 | ① |
| Transformer Block | 12개, Block마다 Head 12개 | ② |
| 출력층과 Softmax | 후보 50,257개 | ③ |
| 가중치 전체 | 약 1억 2,400만 개 | 학습으로 정해진다 |

> Tokenizer: 문장을 Token으로 자르고 번호를 붙이는 도구.
>
> 출력층: 마지막 벡터를 사전의 Token마다 점수 하나로 바꾸는 층.
>
> Softmax: 점수 목록을 0~1 사이, 합이 1인 확률로 바꾸는 함수.

대형 LLM도 이 흐름은 같다. 사전 크기와 벡터 칸 수, Block 수가 커졌고, 위치 정보나 정규화 같은 내부 부품도 일부 바뀌었다(5.2).

---

# 1~4장. 기본 단계를 실제로 해 보면

LLM이 글을 처리하는 기본 단계를 순서대로 짧게 설명하고, 같은 내용을 실제 Tokenizer와 실제 모델로 해 본 결과를 바로 붙인다.

## 예시 문장

```text
입력: 민수는 사과를 좋아하고 지수는 포도를 좋아해. 민수 생일 선물로 뭘 살까?
답:   사과
```

질문 문장에는 '사과'가 없으므로, 모델이 답하려면 앞 문장에서 민수와 사과를 이어야 한다. 이 연결이 어느 단계에서 생기는지 그림을 따라가며 살펴본다. 각 절 맨 위의 작은 그림은 전체 흐름에서 현재 위치를 나타낸다.

실제 모델 실습에는 GPT-2가 영어로 학습한 모델이라 같은 뜻의 영어 문장을 넣었다. 1~4장과 6장의 GPT-2 결과는 모두 이 문장을 넣고 얻은 것이다.

```text
Minsu likes apples and Jisu likes grapes. For Minsu's birthday, I will buy him some
```

## 1. Tokenization

![그림 6](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-06.png)

> 문장을 Token으로 자르고 Token마다 사전 번호를 붙인다.

예전에는 단어 사전을 쓰고 사전에 없는 단어는 '모름'으로 처리했다. 2016년 무렵 번역 모델이 BPE(Byte Pair Encoding. 원래 1994년에 나온 데이터 압축 기법으로, 자주 붙어 나오는 글자 쌍을 하나로 합쳐 가는 방식)를 가져와 쓰기 시작했고, GPT-2는 이를 바이트(컴퓨터가 글자를 저장하는 가장 작은 단위) 단위로 바꿔 어떤 글자든 받을 수 있게 했다. Token은 원래 '표, 대용 화폐'라는 뜻으로, 버스 토큰처럼 무언가를 대신하는 조각을 말한다. 여기서는 글을 대신하는 조각이다.

이 방식 덕분에 모르는 단어가 없어졌고 신조어나 오타도 조각으로 나눠 받을 수 있게 되었다. 다만 학습 데이터에 적게 나온 한국어는 조각 수가 늘어 비용이 커진다.

> 실제로 해 보면.
>
> 같은 예시 문장을 GPT-2와 GPT-4o(OpenAI의 2024년 모델)의 실제 Tokenizer에 넣었다(실습 1).

| 문장 | GPT-2 | GPT-4o |
|---|---|---|
| 민수는 사과를 좋아해. | 26개 | 9개 |
| 인공지능을 공부한다 | 24개 | 6개: [인] [공지] [능] [을] [ 공부] [한다] |

실제 GPT-4o는 '인공지능'을 [인] [공지] [능]으로 자르며, 이는 사람이 생각하는 단어 경계와 맞지 않는다. BPE가 뜻이 아니라 학습 데이터에서 함께 나온 횟수를 기준으로 합치기 때문이다. GPT-2는 한글을 글자 단위도 아닌 바이트 단위로 쪼갠다. 참고로 번호 자체에는 뜻이 없어서, 사과와 포도의 번호가 가깝더라도 우연이다.

## 2. Embedding과 Positional Encoding

![그림 7](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-07.png)

> Token 번호를 벡터로 바꾸고 몇 번째 자리인지를 더한다.

예전에는 단어를 번호표로만 다뤘는데, 2013년 Word2Vec(구글이 발표한 단어 벡터 학습 방법)이 단어를 뜻이 담긴 숫자 줄로 바꾸는 방법을 널리 알렸고 Transformer는 여기에 위치 정보를 더했다. Embed는 '박아 넣다'라는 뜻으로, 단어를 숫자 공간 속 한 점으로 박아 넣는다는 의미이다. 뜻이 비슷한 단어는 가까운 점이 된다.

그 결과 번호만 다르던 단어들이 뜻의 거리를 갖게 되었다. 예를 들어 사과와 포도는 가깝고 민수와는 멀다. 위치를 따로 더하는 이유는 Attention이 문장을 한꺼번에 보기 때문에 순서를 알 수 없어서이다. 위치 정보가 없으면 '민수가 지수를 좋아해'와 '지수가 민수를 좋아해'가 같아진다.

> 과정.
>
> Token ID로 Embedding 표에서 벡터를 꺼내고, 여기에 Positional Encoding을 더해 위치 정보를 넣는다.

![그림 8](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-08.png)

> 실제로 보면.
>
> 위치 값을 만드는 방식은 모델마다 다르다.

| 방식 | 위치 값 | 쓰는 모델 |
|---|---|---|
| 사인·코사인 | 공식으로 계산한다. 학습하지 않는다 | 논문의 Transformer |
| 위치 표 학습 | Token 표처럼 1,024줄 표를 학습한다 | GPT-2 |
| RoPE | 더하지 않고 Attention 안에서 벡터를 자리만큼 회전한다 | Llama 등 최근 모델 대부분 |

> RoPE(Rotary Position Embedding): 위치를 더하는 대신 Attention 안에서 벡터를 자리만큼 회전시켜 순서를 반영하는 방법.
>
> Llama: 메타가 공개한 LLM.

GPT-2는 위치 표가 1,024줄뿐이라 Token 1,024개보다 긴 글은 넣을 수 없다. 벡터 칸 수도 모델마다 달라서 GPT-2는 768칸, Qwen2.5(알리바바가 2024년 공개한 LLM)는 896칸이다(실습 7). 표의 값은 처음에는 무작위이고, 학습하면서 다음 Token을 잘 맞히는 쪽으로 고쳐지며 비슷하게 쓰이는 Token끼리 벡터가 가까워진다.

## 3. Self-Attention

![그림 9](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-09.png)

> 각 Token이 앞쪽 Token 가운데 관련 있는 것을 골라 그 정보를 가져온다.

Attention은 2014~2015년 번역 모델에 처음 붙었을 때만 해도 RNN을 돕는 보조 장치였고, 2017년 Transformer 논문에서 RNN을 빼고 Attention을 중심에 두었다. Attention은 '주의, 주목', Self는 '자기 자신'이라는 뜻이다. 다른 문장이 아니라 같은 문장 안의 단어끼리 서로 주목한다는 의미이다.

이 방식으로 멀리 떨어진 단어도 한 번에 연결할 수 있게 되었고, 문장 전체를 동시에 계산하므로 GPU로 빠르게 돌려 모델을 크게 키울 수 있었다.

> 과정.
>
> Q·K·V를 만들고 점수를 매긴 뒤, Scaling(점수를 벡터 칸 수의 제곱근으로 나눠 크기를 맞추는 것)과 Mask(뒤쪽 가리기)를 거쳐 비율로 바꾼다. 흐름은 아래와 같다.

![그림 10](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-10.png)

뒤쪽 Token을 가리는 이유는 학습 방식에 있다. 학습할 때는 정답 문장 전체를 한꺼번에 넣는데, 뒤쪽을 볼 수 있으면 모델이 다음 Token을 예측하지 않고 답을 그대로 베끼게 된다.

> 실제로 해 보면.
>
> 예시 문장의 영어 문장을 실제 GPT-2에 넣고, 마지막 Block에서 마지막 자리 'some'이 앞쪽 Token에 준 비율을 꺼냈다. GPT-2는 이 계산을 Block마다 12갈래(Head)로 나눠서 하므로, 아래 값은 Head 12개의 평균이다(실습 4-3과 같은 결과).

| Token | M (첫 Token) | buy | apples | him | grapes |
|---|---|---|---|---|---|
| 비율 | 38.8% | 7.6% | 7.5% | 5.4% | 5.4% |

M은 문장 맨 앞 단어 Minsu가 Tokenizer에서 [M] [ins] [u] 세 조각으로 잘리면서 생긴 첫 조각이다. 여기에 38.8%가 몰린 것은 M이라는 글자 때문이 아니라 첫 자리이기 때문이다. GPT 계열 모델은 특별히 볼 곳이 없을 때 남는 비율을 문장의 첫 Token에 몰아 두는 습관이 있으며, 이를 Attention Sink(비율이 고이는 곳)라고 부른다. 그래서 이 값은 의미 있는 값으로 보지 않는다. 첫 Token을 빼면 사는 행동(buy), 두 과일(apples, grapes), 받는 사람(him)을 많이 봤다.

## 4. 확률과 Sampling

![그림 11](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-11.png)

> 마지막 자리 Hidden State로 사전 속 모든 Token의 확률을 내고 하나를 고른다.

다음 말을 확률로 맞힌다는 생각 자체는 오래되었다. 1948년 섀넌(정보 이론을 만든 미국 수학자)이 단어가 이어질 확률로 영어 문장을 만들어 보였고, 휴대폰 자동완성도 같은 방식이다. 달라진 것은 확률을 계산하는 엔진이다. Sampling은 '표본 뽑기'라는 뜻으로, 시식 코너 샘플처럼 전체에서 하나를 뽑는 것을 말한다. Temperature는 '온도'로, 높으면 후보가 고르게 퍼지고 낮으면 1위로 쏠린다.

같은 질문에 매번 조금씩 다른 답이 나오는 이유가 바로 이 단계에 있다. 늘 1위만 고르면 같은 말을 되풀이하기 쉬우므로 확률대로 뽑는다.

> 과정.
>
> Hidden State가 Linear(출력층), Logit, Temperature, Softmax를 거쳐 확률이 되고, 아래 세 방식 중 하나로 다음 Token을 고른다.

| 방식 | 한 줄 설명 |
|---|---|
| Greedy | 매번 확률 1위 하나만 고른다. 뽑기가 없어 항상 같은 결과가 나온다 |
| Top-K | 확률 상위 K개만 후보로 남기고, 그 안에서 확률대로 뽑는다 |
| Top-P | 확률이 높은 순으로 더해 가다 합이 P(예: 0.9)가 될 때까지의 Token만 남기고, 그 안에서 뽑는다 |

![그림 12](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-12.png)

> 실제로 해 보면.
>
> 실제 GPT-2에서 apples의 확률은 Temperature에 따라 아래처럼 바뀐다(실습 4-1과 같은 결과).

| Temperature | 0.5 | 1.0 | 2.0 |
|---|---|---|---|
| apples (1위) 확률 | 80.3% | 16.6% | 0.7% |

Temperature 1.0에서 지수가 좋아하는 grapes는 2.5%로 5위이다. 1위 확률이 16.6%에 그치는 것은 사전에 있는 5만 개 Token에 확률이 나뉘기 때문이다. 그래서 실제로는 Top-K, Top-P처럼 후보를 먼저 줄인 뒤 뽑으며, 세 방식을 실제로 돌린 결과는 실습 5에서 본다.

---

# 5. 현대 LLM의 Transformer: Decoder-Only

1~4장은 2017년 논문에도 있는 기본 단계였다. 이 장부터는 실제 LLM인 GPT 계열을 살펴본다.

2018년에는 GPT-1(OpenAI가 만든 Decoder만 쓴 모델)과 BERT(구글이 만든 Encoder만 쓴 모델)가 같은 해에 나왔고, 처음에는 BERT가 더 주목받았다. 그러나 GPT-2(2019)와 GPT-3(2020)에서 Decoder만 키운 쪽이 글쓰기와 여러 과제를 한 모델로 해내면서 흐름이 넘어왔다. ChatGPT, Llama, Qwen 모두 이 갈래에 속한다.

Encoder는 '부호로 바꾸는 쪽'으로, 문장을 읽어 숫자에 담는다. Decoder는 '부호를 푸는 쪽'으로, 숫자에서 문장을 꺼낸다. Decoder-Only는 이 중 꺼내는 쪽만 쓰는 구조이다. 이로써 번역, 요약, 분류마다 모델을 따로 만들던 방식이 끝났고, 모델 하나에 글로 지시하면 다음 말 이어 쓰기 하나로 모든 과제를 처리하게 되었다. 실습 4(GPT-2)와 실습 7(2024년 Qwen2.5)에서도 같은 질문에 같은 방식으로 답이 나온다.

## 5.1 같은 논문에서 갈라진 세 갈래

![그림 13](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-13.png)

> T5, BART: 각각 구글과 메타가 만든, Encoder와 Decoder를 모두 쓰는 모델.

BERT는 앞뒤를 모두 보고 GPT는 앞쪽만 본다. 지금 쓰는 대화형 LLM은 대부분 GPT처럼 Decoder만 사용하는데, 다음 단어 맞히기 하나로 이해와 생성을 함께 할 수 있고 구조가 단순해 키우기 쉽기 때문이다.

논문의 Decoder에는 Masked Self-Attention(뒤쪽 Token을 가린 채 같은 문장 안에서 하는 Attention)과 Cross-Attention(Decoder가 Encoder의 출력을 참고하는 Attention. 번역에서 원문을 보는 역할) 두 가지가 있다. GPT는 질문과 답을 한 줄로 이어 붙여 넣으므로 Encoder가 없고, 따라서 Cross-Attention도 필요 없어 Masked Self-Attention만 남는다.

## 5.2 논문 구조와 실제 GPT-2의 차이

실습 4에서 돌린 GPT-2는 같은 뼈대를 쓰지만 몇 가지가 다르다. 아래 값은 두 논문과 GPT-2 공개 설정을 기준으로 정리했다.

| 항목 | 논문 Transformer (base) | GPT-2 (124M) | 최근 LLM 예: Llama 3 8B |
|---|---|---|---|
| 구조 | Encoder 6층 + Decoder 6층 | Decoder만 12층 | Decoder만 32층 |
| Attention | Self, Masked Self, Cross | Masked Self 하나 | Masked Self 하나 (Key·Value를 Head 여럿이 나눠 씀) |
| 벡터 칸 수 | 512 | 768 | 4,096 |
| Head 수 | 8 | 12 (Head마다 64칸) | 32 (Key·Value는 8) |
| 사전 크기 | 37,000 | 50,257 | 128,256 |
| 위치 정보 | 사인·코사인 공식 | 위치 표를 학습 (1,024줄) | RoPE (회전) |
| FFN 활성화 함수 | ReLU | GELU | SwiGLU |
| FFN 안쪽 칸 수 | 2,048 | 3,072 (768의 4배) | 14,336 |
| 정규화 위치 | 계산 뒤 (Add 후 Norm) | 계산 앞 (Norm 후 계산, Add) | 계산 앞 (RMSNorm) |
| 입력과 출력 | 원문과 번역문을 따로 넣는다 | 질문과 답을 한 줄로 이어 붙인다 | GPT-2와 같다 |

> Llama 3 8B: 메타의 2024년 모델로, 가중치가 80억(8 Billion) 개.
>
> 활성화 함수: FFN 안에서 값을 그대로 넘길지 줄일지 정하는 함수. ReLU는 음수를 0으로 자르고, GELU는 0 근처에서 꺾이지 않고 부드럽게 줄이며, SwiGLU는 값을 두 갈래로 계산해 한쪽이 다른 쪽을 얼마나 통과시킬지 정한다.
>
> 정규화: 벡터 값의 크기를 일정하게 맞추는 계산. RMSNorm은 평균은 빼지 않고 크기만 맞추는 가벼운 정규화이다.

표의 차이는 대부분 크기를 키우고 부품을 바꾼 것이다. 이 가운데 이유가 가장 분명한 차이는 정규화 위치이다. 논문은 계산 뒤에서, GPT-2는 계산 앞에서 값의 크기를 맞춘다. 계산 앞에서 맞추면 원래 값이 다음 Block까지 그대로 이어지기 때문에 층을 깊게 쌓아도 학습이 무너지지 않는다. 그래서 GPT-2 이후 대부분의 LLM이 이 방식을 쓴다.

![그림 14](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-14.png)

GPT-2에서 최근 LLM으로 오면서 뼈대는 그대로 두고 부품만 바뀌었다. Decoder만 쓰고, 가린 Self-Attention과 FFN을 Block으로 쌓으며, 계산 앞에서 정규화한다는 점은 같다. 달라진 것은 크기, 위치 정보, 활성화 함수, Key·Value를 나눠 쓰는 방식이다. 그래서 이 글의 실습은 GPT-2로 했지만 동작 원리는 최근 모델에도 그대로 적용된다. 다만 1위 확률, Head 번호 같은 숫자는 GPT-2에서만 나온 값이다.

## 5.3 Block을 지나며 답이 생긴다

![그림 15](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-15.png)

> Token마다 가져온 정보를 가공하고 이 묶음을 여러 번 반복한다.

Attention과 Feed Forward Network를 묶은 것을 Transformer Block이라고 하며, Block 하나의 구조는 다음과 같다.

![그림 16](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-16.png)

Attention이 재료를 모으면 Feed Forward Network가 이를 Token마다 따로 가공한다. 이때 학습으로 익힌 패턴 가운데 지금 입력과 맞는 것이 켜지는데, 예시에서는 생일 선물을 고르는 상황이라는 정보가 여기서 생긴다. 계산 결과는 원래 벡터에 덮어쓰지 않고 더하며, 이를 Residual Connection(잔차 연결)이라고 한다. 계산 전에는 값의 크기를 맞추는데, 이것이 Layer Normalization(층 정규화)이다. 두 장치 모두 Block을 깊게 쌓아도 학습이 잘되도록 하기 위한 것이다.

Block 하나를 지날 때 각 Token은 앞쪽 Token에서 정보를 한 번 가져온다. 그런데 '선물'에서 '민수'로, 다시 '민수가 좋아하는 것'으로, 마지막으로 '사과'로 넘어가는 연결은 정보를 여러 번 이어 받아야 완성된다. 그래서 Block을 한 번만 지나서는 부족하고, GPT-2는 12번, 대형 LLM은 수십에서 100여 번 지난다. 아래 그림은 이 생각을 설명하려고 그린 것이다.

![그림 17](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-17.png)

### Hidden State: Block을 지나며 쌓이는 벡터

여러 Block을 지난 결과를 Hidden State라고 부른다. Block은 벡터를 바꿔 끼우지 않고 계산 결과를 더해 가기 때문에 각 자리 벡터에는 Block마다의 결과가 차례로 쌓인다. 다음 Token은 마지막 자리의 Hidden State 하나로 정한다. 실제 GPT-2에서 Block마다 이 벡터를 꺼내 정말 답이 여러 Block에 걸쳐 생기는지 본 결과는 6장 실습 4-2에서 숫자와 함께 보여 준다.

## 5.4 반복해서 문장을 만든다

![그림 18](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-18.png)

> 고른 Token을 맨 끝에 붙이고 다음 Token을 다시 계산한다.

```text
... 뭘 살까? → 사과 → 를 → 추천해요 → [EOS]
```

EOS(End Of Sequence)는 '문장이 끝났다'는 뜻의 특수 Token이다. 모델이 이 Token을 고르거나 미리 정한 최대 길이에 닿으면 반복을 멈추고, 그동안 고른 Token 번호를 다시 글자로 바꾼다(Decoding). 한 가지 덧붙이면, LLM에는 질문을 이해하는 장치와 답을 만드는 장치가 따로 있지 않고 같은 계산을 Token 하나씩 반복할 뿐이다.

---

# 6. 실제 모델로 확인 (실습)

## 6.0 실습과 흐름의 대응

신경망은 오랫동안 안을 들여다볼 수 없는 블랙박스로 불렸으나, 2020년 무렵부터 모델 내부를 들여다보는 연구가 늘었다. GPT-2(2019), Llama(2023), Qwen(2024)처럼 가중치가 공개된 모델이 있어 지금은 노트북에서도 직접 확인할 수 있다. 이 장의 숫자는 설명을 믿는 대신 직접 확인한 것으로, 모두 코드를 실제로 실행한 결과이다.

아래 그림은 각 실습이 전체 흐름의 어느 단계를 확인하는지 나타낸다.

![그림 19](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-19.png)

### 실험 방법

GPT-2와 Qwen2.5 실습은 Hugging Face(공개 AI 모델을 내려받는 사이트)에 올라와 있는 원본 가중치를 그대로 내려받아 썼다. 가중치를 고치거나 추가로 학습시키지 않았고, 우리가 정한 것은 입력 문장 하나뿐이다. 결과는 출력된 그대로 옮겼으며 원하는 결과가 나올 때까지 여러 번 돌려 고르지 않았다. 원본 출력은 코드 옆에 `_result.txt` 파일로 남겨 두었고, 실행 화면 가운데 필요한 부분은 이 글 맨 뒤 부록에 옮겼다. 실습 2만은 계산 과정을 보이려고 사람이 가중치를 직접 정한 예시이다.

코드는 `docs/simple/practice`에 있으며 GPU 없이 노트북의 CPU(일반 컴퓨터의 중앙 처리 장치)로 실행된다. 코드의 줄마다 무엇을 하는지 주석을 달아 두었다.

```text
cd docs/simple/practice
npm install && node 01_tokenizer.mjs   # 실습 1
python3 02_attention.py                # 실습 2 (numpy 필요)
python3 03_next_token.py               # 실습 3 (numpy 필요)
python3 03_learning_trace.py           # 실습 3 학습 중 확률 기록
pip install torch transformers
python3 04_trace.py                    # 실습 4-0 (처음 실행 때 GPT-2 약 500MB 다운로드)
python3 04_gpt2.py                     # 실습 4
python3 05_sampling.py                 # 실습 5
python3 06_heads.py                    # 실습 6
python3 07_qwen.py                     # 실습 7 (처음 실행 때 Qwen2.5 약 1GB 다운로드)
```

> npm: JavaScript 도구를 설치하는 프로그램.
>
> numpy: 파이썬의 숫자 계산 도구.
>
> torch(PyTorch), transformers: 신경망을 돌리는 파이썬 도구와, 공개 모델을 내려받아 쓰게 해 주는 도구.

실습 2~7은 같은 코드를 한 번 더 실행해 같은 숫자가 나오는 것을 확인했다(GPT-2, Qwen2.5 모두 CPU, float32. float32는 소수를 32비트로 계산하는 방식이다).

Windows에서는 python3 대신 `python -X utf8`로 실행한다. python3가 아무 출력 없이 끝나거나 한글 출력이 깨지는 경우가 있기 때문이다.

## 실습 1. Tokenizer 비교

![그림 20](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-20.png)

같은 문장을 GPT-2와 GPT-4o의 실제 Tokenizer로 잘라 비교했다(`01_tokenizer.mjs`).

| 문장 | GPT-2 | GPT-4o |
|---|---|---|
| 민수는 사과를 좋아해. | 26개 | 9개: [민] [수] [는] [ 사] [과] [를] [ 좋아] [해] [.] |
| Minsu likes apples. | 6개: [M] [ins] [u] [ likes] [ apples] [.] | 5개: [M] [insu] [ likes] [ apples] [.] |
| 인공지능을 공부한다  | 24개 | 6개: [인] [공지] [능] [을] [ 공부] [한다] |

GPT-2는 영어 위주로 사전을 만들었기 때문에 한글 한 글자가 바이트 단위로 2~3개씩 쪼개진다. 반면 GPT-4o는 사전이 커서 한글도 글자나 단어 단위로 자른다. 즉, 같은 내용이라도 언어에 따라 Token 수가 다르고 그에 따라 비용과 속도도 달라진다.

## 실습 2. Self-Attention 직접 계산

![그림 21](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-21.png)

'민수 는 사과 를 좋아하고' 다섯 Token에 3장의 Self-Attention 계산을 numpy로 적용했다(`02_attention.py`). 이 실습은 실제 모델이 아니다. Query 가중치는 동사가 사람과 과일을 찾도록 사람이 직접 정했으며, 실제 모델에서는 이 값을 학습으로 정한다.

| Query \ 참고한 Token | 민수 | 는 | 사과 | 를 | 좋아하고 |
|---|---|---|---|---|---|
| 민수 | 1.00 | | | | |
| 는 | 0.50 | 0.50 | | | |
| 사과 | 0.33 | 0.33 | 0.33 | | |
| 를 | 0.25 | 0.25 | 0.25 | 0.25 | |
| 좋아하고 | 0.32 | 0.12 | 0.32 | 0.12 | 0.12 |

빈칸은 뒤쪽 Token이라 가려진 자리이고, 행마다 합은 1이다. 찾는 대상이 없는 Token은 볼 수 있는 Token을 고르게 섞지만, '좋아하고'는 민수와 사과에 더 큰 비율을 준다. 그 결과 벡터는 [사람 0.32, 과일 0.32, 조사 0.24, 동사 0.12]가 되어 동사 자리에 주어와 목적어 정보가 모인다.

## 실습 4. 실제 GPT-2로 확인

![그림 22](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-22.png)

GPT-2는 영어로 학습한 모델이므로 같은 뜻의 영어 문장을 넣었다(`04_gpt2.py`).

```text
Minsu likes apples and Jisu likes grapes. For Minsu's birthday, I will buy him some
```

이 문장은 Token 23개로 잘리며, 'Minsu'는 [M] [ins] [u] 세 조각이 된다. 아래 숫자는 Windows PC(CPU)에서 직접 실행한 결과이며, 같은 모델에 같은 문장을 넣으면 누가 돌려도 같은 값이 나온다.

| 원리에서 본 것 | 실습 4에서 확인하는 것 |
|---|---|
| 4장. 모든 후보에 확률을 매긴다 | 다음 Token 상위 5개와 Temperature |
| 5.3 Block을 여러 번 지나며 연결이 생긴다 | Block마다 apples의 확률 |
| 3장. 앞쪽 Token에서 정보를 가져온다 | 마지막 자리가 많이 본 Token |
| 5.4 고른 Token을 붙여 반복한다 | 이어 쓰기 |

## 실습 4-0. 글자가 숫자로 바뀌어 답이 되기까지

![그림 23](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-23.png)

예시 문장이 모델 안에서 어떤 데이터로 바뀌는지 차례로 따라가면 다음과 같다(`04_trace.py`).

| 단계 | 모델 안의 데이터 |
|---|---|
| 글자 | Minsu likes apples ... I will buy him some |
| 조각과 번호 | 조각 23개마다 사전 번호(Token ID)가 붙는다. 예: ' apples'는 22514번 |
| 벡터 | 번호마다 숫자 768개로 된 줄을 꺼내고 자리 정보를 더한다. 줄이 23개 생긴다 |
| Block 12개 | 줄 23개가 Block을 차례로 지난다. 줄의 개수와 길이는 그대로이다 |
| 점수 | 마지막 자리('some')의 줄로 사전의 50,257개 Token마다 점수를 매긴다 |
| 확률 | 점수를 합이 100%인 확률로 바꾼다. 1위는 apples 16.6%이다 |

번호 자체에는 뜻이 없고, 뜻은 번호로 꺼낸 768개 숫자 줄에 담긴다. Block을 지나도 줄의 개수와 길이가 바뀌지 않기 때문에 Block을 12번 이어 쌓을 수 있다. 고른 Token을 맨 끝에 붙이면 입력이 24개가 되고, 같은 계산을 처음부터 다시 한다.

## 실습 4-1. 다음 Token 확률과 Temperature

![그림 24](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-24.png)

| 순위 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 다음 Token | apples | . | apple | of | grapes |
| 확률 | 16.6% | 4.4% | 3.0% | 2.9% | 2.5% |

GPT-2는 민수가 좋아하는 apples를 1위로, 지수가 좋아하는 grapes를 5위로 놓았다. 두 과일 모두 문장에 나왔지만 apples의 확률이 6배 넘게 높다. 1위 확률이 16.6%로 낮아 보이는 것은 some 뒤에 올 수 있는 말이 5만 개 후보 안에 많기 때문이다.

다음은 같은 점수에 Temperature만 바꾼 결과이다.

| Temperature | apples | . | apple |
|---|---|---|---|
| 0.5 | 80.3% | 5.6% | 2.7% |
| 1.0 | 16.6% | 4.4% | 3.0% |
| 2.0 | 0.7% | 0.3% | 0.3% |

순위는 그대로이고 쏠림 정도만 달라진다. 0.5에서는 apples에 80%가 몰리고, 2.0에서는 확률이 5만 개 후보 전체로 퍼져 1위도 1%가 되지 않는다. Temperature를 높이면 답이 다양해지는 이유가 여기에 있다.

## 실습 4-2. Block을 지나며 답이 생긴다

5.3에서 Block을 여러 번 지나야 답이 생긴다고 했다. 정말 그런지 보려고, Block 하나를 지날 때마다 마지막 자리('some')의 벡터를 꺼내 출력층에 바로 넣어 보았다. 이렇게 하면 '이 시점에서 답을 고르라고 하면 무엇을 고를까'를 알 수 있다. 계산 중간에 렌즈를 대고 들여다본다는 뜻에서 이 방법을 Logit Lens라고 부른다. 원래 중간 벡터는 출력층에 넣으라고 만든 값이 아니므로 결과는 대략적인 참고값이다.

![그림 25](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-25.png)

| 지난 Block 수 | 그 시점의 1위 | apples | grapes |
|---|---|---|---|
| 0 (Embedding만) | mathemat | 0.00% | 0.00% |
| 1 | very | 0.00% | 0.00% |
| 2~8 | place | 0.00% | 0.00% |
| 9 | place | 0.53% | 0.11% |
| 10 | apples | 19.38% | 1.47% |
| 11 | apples | 64.55% | 4.85% |
| 12 (최종 출력) | apples | 16.6% | 2.5% |

표를 위에서부터 읽으면, 앞쪽 9개 Block을 지나는 동안은 1위가 place 같은 엉뚱한 단어이고 apples는 0%에 가깝다. 이 시점에 답을 고르게 하면 아직 apples를 고르지 못한다는 뜻이다. 이 구간에서 모델이 정확히 무슨 일을 하는지는 이 방법으로 알 수 없으며, 앞 단어들의 정보를 모으는 중이라고 짐작할 뿐이다. 10번째 Block을 지나자 apples가 처음 1위(19.38%)로 올라서고, 11번째에서는 64.55%까지 오른다. 마지막 Block을 지나며 16.6%로 줄지만 1위는 그대로이다. 즉, 답은 처음부터 있던 것이 아니라 Block을 여러 번 지난 뒤에야 나타났다.

원본 출력 파일의 Block 12 줄에는 처음 코드의 오류(정규화를 두 번 적용)로 다른 값이 찍혀 있다. Block 12를 지난 값은 최종 출력과 같아야 하므로 표에는 실습 4-1의 최종 출력 값을 넣었고, 코드는 고쳐 두었다.

## 실습 4-3. 마지막 자리가 본 Token과 이어 쓰기

![그림 26](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-26.png)

아래는 마지막 Block에서 마지막 자리 'some'이 앞쪽 Token에 준 Attention 비율로, Head 12개의 평균이다.

| Token | M (첫 Token) | buy | apples | him | grapes |
|---|---|---|---|---|---|
| 비율 | 38.8% | 7.6% | 7.5% | 5.4% | 5.4% |

M은 문장 맨 앞 단어 Minsu가 [M] [ins] [u]로 잘리면서 생긴 첫 조각이다. 첫 Token에 38.8%가 몰린 것은 M의 뜻 때문이 아니라 첫 자리이기 때문이다. GPT 계열 모델은 특별히 볼 곳이 없을 때 남는 비율을 첫 Token에 몰아 두는 것으로 알려져 있으며(Attention Sink), 그래서 의미 있는 값으로 보지 않는다. 나머지 중에서는 사는 행동(buy), 받는 사람(him), 두 과일(apples, grapes)을 많이 봤다. 실습 2에서 동사가 주어와 목적어를 찾던 것과 같은 모습이다. 다만 이 표는 12개 Block 가운데 마지막 하나만 본 것이고, 민수와 apples를 잇는 일은 앞쪽 Block들이 나눠서 한다.

다음은 Greedy 방식, 즉 매번 확률 1위 Token만 골라 10개를 이어 쓴 결과이다. 생략한 것 없이 모델이 낸 10개 Token을 그대로 옮겼다.

```text
... I will buy him some apples.

I will buy him some apples
```

10개는 [ apples] [.] [줄바꿈] [줄바꿈] [I] [ will] [ buy] [ him] [ some] [ apples]이다. 빈 줄은 줄바꿈 Token 두 개가 찍힌 것이다. 첫 Token으로 apples를 고르고 마침표로 문장을 끝낸 뒤, 그 뒤로는 앞 문장을 그대로 되풀이한다. 124M은 GPT-3(1,750억 개)보다 1,000배 이상 작은 모델이라 이런 반복이 자주 나오며, 1위만 고르는 Greedy 방식도 반복을 부추긴다.

## 실습 5. Greedy, Top-K, Top-P 비교

![그림 27](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-27.png)

4장의 세 방식을 실습 4와 같은 문장으로 실제 GPT-2에서 실행했다(`05_sampling.py`). 세 방식을 다시 한 줄씩 정리하면 다음과 같다.

| 방식 | 한 줄 설명 |
|---|---|
| Greedy | 매번 확률 1위 하나만 고른다. 뽑기가 없어 항상 같은 결과가 나온다 |
| Top-K | 확률 상위 K개만 후보로 남기고, 그 안에서 확률대로 뽑는다 |
| Top-P | 확률이 높은 순으로 더해 가다 합이 P가 될 때까지의 Token만 남기고, 그 안에서 뽑는다 |

Top-K와 Top-P는 컴퓨터가 만든 무작위 수로 뽑는다. 이 무작위 수는 seed(시드, 씨앗)라는 시작 번호에서 정해진 순서대로 만들어지기 때문에, seed를 같은 번호로 고정하면 누가 몇 번을 돌려도 같은 순서로 뽑혀 같은 문장이 나온다. 여기서는 seed를 0, 1, 2로 고정해 세 번 뽑았다. 다른 사람이 같은 코드를 돌려 같은 결과가 나오는지 확인할 수 있게 하려는 것이다.

세 방식은 모두 공개 도구(transformers)에 이미 들어 있어서, 직접 만들지 않고 옵션 값만 바꿔 골랐다.

아래 숫자는 Windows PC(CPU)에서 직접 실행한 결과이다.

먼저 첫 Token에서 방식마다 남는 후보 수와 그 후보들의 확률 합이다.

| 방식 | 남는 후보 | 남은 확률 합 |
|---|---|---|
| Greedy (Top-K 1) | 1개 | 16.6% |
| Top-K 5 | 5개 | 29.4% |
| Top-K 50 | 50개 | 55.4% |
| Top-P 0.5 | 33개 | 50.2% |
| Top-P 0.9 | 1,118개 | 90.0% |

같은 K라도 남는 확률은 상황에 따라 다르며, 이 문장에서는 상위 50개를 남겨도 확률의 절반 남짓만 담긴다. Top-P는 확률 합을 기준으로 자르기 때문에 후보 수가 33개에서 1,118개까지 달라진다. 1위 apples도 16.6%에 그칠 만큼 확률이 넓게 퍼져 있어서, 합 90%를 채우려면 낮은 확률의 Token을 1,000개 넘게 담아야 하기 때문이다.

Top-K 5로 후보를 남긴 뒤에는 남은 후보끼리 확률을 다시 나눈다. 다섯 개의 합이 29.4%이므로 각 확률을 이 합으로 나누어 합이 100%가 되게 한다(반올림 전 값으로 계산해 표의 숫자로 나누면 소수점이 조금 다르다).

| 후보 | apples | . | apple | of | grapes |
|---|---|---|---|---|---|
| 원래 확률 | 16.6% | 4.4% | 3.0% | 2.9% | 2.5% |
| Top-K 5 뒤 | 56.3% | 14.9% | 10.3% | 9.9% | 8.6% |

다음은 같은 문장을 방식마다 12 Token씩 이어 쓴 결과이다.

| 방식 | 이어 쓴 결과 (... buy him some 다음) |
|---|---|
| Greedy | apples. / I will buy him some apples. I |
| Top-K 50 | ① sweets when he wakes up. ② apple juice. It's not just for Christmas ③ apples and eat a few of them. He is excited. |
| Top-P 0.9 | ① along with seven more pretty Girls... [EOS] ② apple custard instead of ones. ③ raisins and eat them each night. |
| 전체에서 뽑기 | Top-P 0.9와 같음 |

Top-P 0.9 ①의 [EOS]는 GPT-2의 EOS(End Of Sequence) Token인 `<|endoftext|>`가 뽑혀 거기서 문장이 끝났다는 표시이다.

결과가 이렇게 나온 이유는 다음과 같다. Greedy는 매번 1위만 고르므로 몇 번을 돌려도 같은 문장이 나오고, 한 번 문장을 끝낸 뒤에는 앞 문장을 되풀이한다. Top-K 50은 상위 50개 안에서만 뽑기 때문에 돌릴 때마다 다른 문장이 나오면서도 세 문장 모두 살 물건(sweets, apple juice, apples)으로 자연스럽게 이어졌다. Top-P 0.9는 후보가 1,118개나 되어 확률이 낮은 엉뚱한 Token도 뽑힐 수 있고, 실제로 문맥에서 먼 문장(① along with seven more pretty Girls)이 나왔다. Top-P 0.9와 전체에서 뽑기의 결과가 같은 것은 우연이 아니다. PyTorch(신경망을 돌리는 파이썬 도구)의 뽑기 방식에서는 seed가 같으면 뽑힌 Token이 상위 90% 안에 있는 한 꼬리를 잘라도 같은 Token이 뽑힌다. 이번 세 번은 모두 그 범위 안에서 뽑혔다.

## 실습 6. Head 144개가 보는 곳

![그림 28](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-28.png)

Multi-Head Attention은 Head마다 서로 다른 관점에서 계산한다고 알려져 있다. 실제 GPT-2의 Head 144개가 정말 서로 다른 곳을 보는지 확인했다(`06_heads.py`).

아래 숫자는 Windows PC(CPU)에서 직접 실행한 결과이다.

Head 144개의 평균을 보면 각 자리는 비율의 56.2%를 첫 Token에 둔다. 실습 4-3에서 본 Attention Sink가 마지막 Block에서만 나타나는 것이 아니라 모델 전체에서 나타난다는 뜻이다.

바로 앞 Token만 보는 Head도 따로 있다.

| Head | 바로 앞 Token에 준 비율 (평균) |
|---|---|
| Block 5 Head 12 | 100.0% |
| Block 3 Head 3 | 56.3% |
| Block 4 Head 8 | 43.2% |

Block 5의 Head 12는 어느 자리에서든 바로 앞 Token만 보며, 문장 순서를 옮겨 주는 역할로 보인다.

다음은 마지막 자리 'some'이 첫 Token을 제외하고 가장 많이 본 Token을 Block별로 센 결과이다.

| Block | 가장 많이 본 Token (Head 12개 기준) |
|---|---|
| 1 | some 자기 자신 6개. 나머지 6개는 For, ., apples, 쉼표, I, likes가 하나씩 |
| 6 | him 4개, buy 2개, . 2개, apples 1개 등 |
| 12 | apples 4개, buy 3개, grapes 2개 등 |

앞쪽 Block에서는 대부분 자기 자신을 보고, 중간 Block에서는 받는 사람(him)과 행동(buy)을, 마지막 Block에서는 과일(apples, grapes)과 buy를 본다. Head마다, 또 Block마다 보는 곳이 다르다는 것을 확인할 수 있다.

마지막 자리가 apples를 가장 많이 본 Head는 다음과 같다.

| Head | apples에 준 비율 |
|---|---|
| Block 11 Head 8 | 42.2% |
| Block 9 Head 4 | 41.5% |
| Block 11 Head 1 | 38.9% |

apples를 많이 보는 Head는 Block 9와 11에 몰려 있어, 실습 4-2에서 apples가 1위로 올라선 시점(Block 10)과 가깝다. 다만 이 Head들이 apples를 1위로 만든 원인인지는 이 실험으로 알 수 없고, 시점이 겹친다는 것까지만 말할 수 있다.

## 실습 7. 최근 모델 Qwen2.5와 비교

![그림 29](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-29.png)

실습 4의 1)~3)을 2024년에 나온 작은 오픈소스 모델 Qwen2.5-0.5B로 똑같이 진행했다(`07_qwen.py`). 0.5B는 가중치가 약 5억(0.5 Billion) 개라는 뜻이다. Qwen2.5는 5.2 표에 나온 최근 LLM 부품(RoPE, RMSNorm, SwiGLU, Key·Value 나눠 쓰기)을 쓰는 모델이다. 아래 숫자는 Windows PC(CPU)에서 직접 실행한 결과이다.

| | GPT-2 (2019) | Qwen2.5-0.5B (2024) |
|---|---|---|
| 가중치 | 1억 2,400만 개 | 4억 9,400만 개 |
| Block 수 | 12 | 24 |
| 사전 크기 | 50,257 | 151,936 |
| 예시 문장의 Token 수 | 23개 | 23개 (같은 조각) |
| 다음 Token 1위 | apples 16.6% | apples 42.6% |
| grapes | 2.5% (5위) | 24.6% (2위) |
| 상위 5개 | apples, ., apple, of, grapes | apples, grapes, fruits, fruit, of |
| apples가 1위로 올라선 시점 | 12개 중 10번째 Block | 24개 중 22번째 Block |

Qwen2.5는 상위 5개 가운데 4개가 과일로, 선물로 과일을 산다는 문맥을 GPT-2보다 확실히 잡았다. apples도 42.6%로 GPT-2의 2.5배이다. 그러나 grapes 역시 24.6%로 높다. 민수가 좋아하는 것과 지수가 좋아하는 것을 가르는 정도(apples와 grapes의 비율)를 보면 GPT-2가 6.6배, Qwen2.5가 1.7배로, 큰 모델이 모든 면에서 나은 것은 아니다.

Block별 기록은 GPT-2와 같은 모양이다. 앞쪽 20개 Block에서는 apples가 거의 0%이고 1위도 뜻 없는 Token이다. 그러다 20번째 Block에서 1위가 gifts(선물), 21번째에서 fruits(과일), 22번째에서 apples(사과)로 바뀌며, 선물에서 과일로, 과일에서 사과로 좁혀 가는 순서가 그대로 드러난다. 5.3에서 설명용으로 그린 여러 단계를 건너는 연결과 같은 모습으로, 부품이 바뀌어도 동작 원리는 같다는 것을 실제 모델로 확인했다.

---

# 7. 학습

예전에는 사람이 정답을 붙인 데이터로 과제마다 따로 학습했지만, GPT 계열은 글 자체에서 다음 단어를 정답으로 삼는다. 2020년에는 모델과 데이터를 키우면 성능이 예측한 만큼 오른다는 결과(Scaling Law, 규모의 법칙)가 나왔고, 2022년 ChatGPT는 그 위에 사람의 평가로 추가 학습을 했다.

학습(Training)은 '훈련'이라는 뜻으로, 문제를 풀고 채점해서 틀린 만큼 고치는 일을 반복하는 것이다. Loss는 '잃은 점수', 즉 틀린 정도를 말한다. 이 방식으로 사람이 정답지를 만들 필요가 줄었다. 인터넷의 글이 그대로 문제집이 되면서 쓸 수 있는 데이터가 크게 늘었고, 모델을 키우는 경쟁이 시작되었다. 실습 3에서는 문장 4개로 작은 모델을 학습해 Loss가 실제로 줄어드는 것을 확인한다.

## 7.1 학습과 사용

![그림 30](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-30.png)

| | 학습 | 사용 |
|---|---|---|
| 하는 일 | 다음 Token을 맞히게 하고 Loss를 줄이는 쪽으로 가중치를 고친다 | 고정된 가중치로 계산한다 |
| 비용 | GPU 수천 개로 수 주에서 수개월 | 질문마다 계산 한 번씩 |

다음 Token 맞히기를 수조 개 Token 분량의 글로 반복하면 문법, 대명사가 가리키는 대상, 사실 관계 같은 패턴이 가중치에 담긴다. 대화형 LLM은 그 뒤에 질문과 답변 예시, 사람의 평가로 추가 학습을 거친다. 실습 3에서는 문장 4개로 작은 모델을 직접 학습해 Loss가 2.20에서 0.16까지 줄어드는 것을 확인했다.

이 글의 GPT-2와 Qwen2.5 실습은 사용 단계만 다루었고, 가중치를 고치는 추가 학습(Fine-tuning, 이미 학습된 모델을 특정 목적에 맞게 조금 더 학습시키는 것)은 하지 않았다. Temperature나 Top-K를 바꾼 것도 고르는 방식만 바꾼 것이라 가중치는 그대로이다. 학습을 직접 해 본 것은 실습 3의 작은 모델뿐이다.

## 7.2 실습 3. 다음 Token 예측 학습

![그림 31](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-31.png)

문장 4개로 아주 작은 모델 두 개를 학습했다(`03_next_token.py`). Transformer가 아닌 한 층짜리 모델이지만, 다음 Token을 맞히고 Loss를 줄이는 학습 방식은 LLM과 같다.

```text
민수 는 사과 를 좋아해 .     지수 는 포도 를 좋아해 .
민수 는 사과 를 샀다 .       지수 는 포도 를 샀다 .
```

| 학습 횟수 | 0 | 10 | 50 | 200 | 500 |
|---|---|---|---|---|---|
| 모델 A Loss | 2.20 | 1.48 | 0.55 | 0.33 | 0.30 |
| 모델 B Loss | 2.20 | 1.31 | 0.42 | 0.20 | 0.16 |

같은 학습 과정에서 '민수 는 ___' 다음 확률이 어떻게 바뀌는지도 기록했다(`03_learning_trace.py`). Loss가 줄어든다는 것이 실제로 무엇을 의미하는지 아래 기록에서 볼 수 있다.

![그림 32](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-32.png)

| 학습 횟수 | 0 | 10 | 50 | 200 | 500 |
|---|---|---|---|---|---|
| 모델 A: 사과 / 포도 | 11% / 11% | 21% / 21% | 40% / 40% | 48% / 48% | 49% / 49% |
| 모델 B: 사과 / 포도 | 11% / 11% | 24% / 19% | 60% / 24% | 86% / 10% | 94% / 5% |

처음에는 가중치가 모두 0이라 사전의 9개 Token이 똑같이 11%이다. 학습할수록 모델 B는 사과 쪽으로 기우는 반면, 모델 A는 사과와 포도가 함께 오르다가 49%에서 멈춘다. 앞에 민수가 있었다는 정보를 받지 못하기 때문이다. 학습을 아무리 많이 해도 입력에 구분할 정보가 없으면 구분할 수 없다.

| 입력 | 모델 A | 모델 B |
|---|---|---|
| 민수 는 ___ | 사과 49%, 포도 49% | 사과 94%, 포도 5% |
| 지수 는 ___ | 사과 49%, 포도 49% | 포도 94%, 사과 5% |
| 민수 는 사과 를 ___ | 좋아해 49%, 샀다 49% | 좋아해 49%, 샀다 49% |

모델 A는 바로 앞의 '는'만 보기 때문에 민수인지 지수인지 알 수 없고, 모델 B는 앞의 '민수'까지 보기 때문에 사과를 고른다. 이 결과는 앞쪽 정보를 가져오는 일이 왜 필요한지 보여 주며, Transformer에서는 이 일을 Self-Attention이 맡는다. 한편 '좋아해'와 '샀다'는 학습 문장에서 실제로 반반이었으므로, 모델도 본 것 이상은 알 수 없다.

다음은 모델 B의 '민수 는 ___'에 Temperature를 바꿔 본 결과이다(반올림 값).

| Temperature | 사과 | 포도 |
|---|---|---|
| 0.5 | 100% | 0% |
| 1.0 | 94% | 5% |
| 2.0 | 66% | 15% |

---

## 정리

![그림 33](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-33.png)

| 단계 | 하는 일 | 예시에서 |
|---|---|---|
| Token | 문장을 조각내고 번호를 붙인다 | '민수는 사과를 좋아해.'가 9~26개 번호로 |
| Embedding과 위치 | 번호를 벡터로 바꾸고 자리를 더한다 | 사과와 포도가 비슷한 벡터가 된다 |
| Self-Attention | 앞쪽 Token에서 관련 정보를 가져온다 | 마지막 자리가 buy, apples, him을 많이 본다 |
| FFN과 Block 반복 | 가져온 정보를 가공하고 여러 번 반복한다 | 실제 GPT-2에서 10번째 Block에 apples가 1위로 |
| 확률과 다음 Token | 모든 후보에 확률을 매기고 하나를 고른다 | 실제 GPT-2에서 apples 16.6%로 1위 |
| 반복 | 고른 Token을 붙이고 다시 계산한다 | 사과 → 를 → 추천해요 |

Transformer는 문장 전체를 한꺼번에 계산하는 구조로 언어 모델을 크게 키울 수 있게 했고, LLM은 그 위에서 다음 Token 하나를 고르는 계산을 반복해 답을 만든다.

## 더 해 볼 것

| 도구 | 해 볼 것 |
|---|---|
| Transformer Explainer (poloclub.github.io/transformer-explainer) | 브라우저에서 GPT-2에 문장을 넣고 Attention 비율과 Temperature 효과를 눈으로 본다 |
| Tiktokenizer (tiktokenizer.vercel.app) | 실습 1을 웹에서 다른 문장과 모델로 해 본다 |
| build-nanogpt (github.com/karpathy/build-nanogpt) | GPT-2를 코드로 처음부터 만들어 학습한다. GPU가 있으면 좋다 |

---

# 부록. 자세히 보기

본문을 읽는 데 꼭 필요하지는 않지만, 구조나 숫자를 더 자세히 확인하고 싶을 때 보는 자료이다.

## 부록 A. 5.2 차이의 의미와 정규화 위치

### A.1 차이마다 무슨 의미인가

표의 차이는 바꾼 이유가 분명한 것과, 실험에서 결과가 더 좋아서 바꾼 것으로 나뉜다. 이유가 분명한 것은 다음과 같다.

| 항목 | 바뀌어서 생긴 차이 |
|---|---|
| Decoder만 쓴다 | 이어 쓰기 하나로 번역, 요약, 대화를 모두 처리하므로 과제마다 구조를 바꿀 필요가 없다(5.1) |
| Cross-Attention이 없다 | 원문을 따로 받는 Encoder가 없으니 참고할 대상도 없다. 질문은 같은 줄 앞쪽에 있으므로 가린 Self-Attention으로 본다 |
| 크기(Block 수, 벡터 칸 수, Head 수) | 클수록 담을 수 있는 패턴이 많아지고 계산량도 커진다. 모델을 키울수록 성능이 오른다는 결과가 7장의 Scaling Law이다 |
| 사전 크기 | 사전이 크면 같은 문장이 더 적은 Token으로 잘려 빠르고 싸다(실습 1에서 26개와 9개). 대신 Token 표가 커진다 |
| 위치 정보 | GPT-2의 위치 표는 1,024줄이라 그보다 긴 글을 받지 못한다. RoPE는 Token 사이 거리를 회전 각도로 넣기 때문에 더 긴 글로 늘리기 쉽다 |
| Key·Value 나눠 쓰기 | 답을 만들 때 앞 Token의 Key·Value를 저장해 두고 다시 쓰는데, Head 여럿이 한 벌을 나눠 쓰면 저장 공간이 줄어 빨라진다. 성능 손실은 작다고 보고되었다 |
| 정규화 위치 | 아래에서 따로 설명한다 |

활성화 함수(ReLU, GELU, SwiGLU)는 실험에서 성능이 조금 더 좋아서 바뀐 경우이다. SwiGLU를 제안한 논문도 왜 잘 되는지는 설명하지 못한다고 적었다. 그래서 이 차이는 '이렇게 바뀌었다'는 사실까지만 말할 수 있다.

### A.2 정규화를 계산 앞에서 하면 무엇이 다른가

논문의 Add & Norm은 계산 뒤 정규화(Post-LN)이고, GPT-2는 계산 앞 정규화(Pre-LN)이다. 두 방식의 차이는 더하기 길, 즉 계산 결과를 원래 벡터에 더하는 길(Residual Connection) 위에 정규화가 끼어 있느냐에 있다.

![그림 34](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-34.png)

| | 계산 뒤 정규화 (논문, Post-LN) | 계산 앞 정규화 (GPT-2, Pre-LN) |
|---|---|---|
| 더하기 길 | 더한 뒤 매번 정규화를 거치므로 원래 값이 Block마다 바뀐다 | 원래 값이 정규화를 거치지 않고 마지막 Block까지 그대로 이어진다 |
| 깊게 쌓을 때 | 층이 깊으면 학습 초반이 불안정해서, 학습률을 처음에 아주 작게 두고 천천히 올려야(warmup) 한다 | warmup에 덜 민감하고 수십~100여 층까지 안정적으로 학습된다 |
| 대가 | 깊게 쌓기 어렵다 | 계산 결과가 Block마다 더해지기만 해서 값이 점점 커지므로 마지막 Block 뒤에 정규화를 한 번 더 둔다. 뒤쪽 Block일수록 Block 하나의 영향이 작아진다는 보고도 있다 |
| 최종 성능 | 학습만 잘되면 조금 더 좋다는 보고가 있다 | 대부분의 LLM이 이 방식을 쓴다 |

> 학습률: 틀린 만큼 가중치를 한 번에 얼마나 고칠지 정하는 값.
>
> warmup: 학습 초반에 학습률을 0에 가깝게 두었다가 조금씩 올리는 방법.

즉, 계산 앞 정규화는 최종 성능을 조금 내주는 대신 깊게 쌓아도 학습이 무너지지 않는 쪽을 택한 것이다. 층을 수십 개 쌓는 LLM에는 이쪽이 유리해서 GPT-2 이후 대부분의 LLM이 이 방식을 쓴다. GPT-2의 마지막 Block 뒤에 있는 정규화(ln_f)가 표에서 말한 '한 번 더 두는 정규화'이며, 실습 4-2의 Logit Lens도 중간 벡터에 이 정규화를 붙여 계산했다.

## 부록 B. 실습 4-0 Token ID와 데이터 모양

예시 문장을 GPT-2 Tokenizer로 자르면 다음과 같다.

```text
자리  조각          Token ID
 0   'M'           44
 1   'ins'         1040
 2   'u'           84
 3   ' likes'      7832
 4   ' apples'     22514
 5   ' and'        290
 6   ' J'          449
 7   'isu'         46313
 8   ' likes'      7832
 9   ' grapes'     36656
10   '.'           13
11   ' For'        1114
12   ' M'          337
13   'ins'         1040
14   'u'           84
15   "'s"          338
16   ' birthday'   10955
17   ','           11
18   ' I'          314
19   ' will'       481
20   ' buy'        2822
21   ' him'        683
22   ' some'       617
```

Token ID는 사전(50,257개)에서 그 조각이 몇 번째인지 나타내는 번호이고, 번호 자체에는 뜻이 없다. 같은 조각은 언제나 같은 ID가 된다. 예를 들어 ' likes'는 3번과 8번 자리에 두 번 나오며 둘 다 7832이다. 다만 앞에 공백이 붙은 ' M'(337)과 문장 맨 앞의 'M'(44)은 서로 다른 조각이다. 모델에는 이 23개 번호가 [1, 23] 모양, 즉 문장 1개에 Token 23개짜리 정수 묶음으로 들어간다.

이 번호가 출력까지 가는 동안 데이터 모양은 아래처럼 바뀐다. 모양은 가중치 값과 상관없이 모델 설정으로 정해진다.

| 단계 | 데이터 모양 | 뜻 |
|---|---|---|
| 입력 (input_ids) | [1, 23] | 문장 1개, Token 23개의 번호 |
| Token 표 (wte) | [50257, 768] | 사전의 Token마다 768칸 벡터 한 줄 |
| 위치 표 (wpe) | [1024, 768] | 자리마다 768칸 벡터 한 줄 |
| Embedding 결과 | [1, 23, 768] | Token 23개마다 768칸 벡터. Token 표의 줄과 위치 표의 줄을 더한 값 |
| Query·Key·Value | [1, 23, 2304] → Head별 [1, 12, 23, 64] | 768칸씩 세 벌을 한꺼번에 만든 뒤, Head 12개가 64칸씩 나눠 쓴다 |
| Attention 비율 | [1, 12, 23, 23] | Head마다 23×23 표. 실습 2의 표와 같은 모양이다 |
| FFN 안쪽 | [1, 23, 3072] | 768칸을 4배로 넓혀 가공한 뒤 다시 768칸으로 줄인다 |
| Block 출력 | [1, 23, 768] | 들어갈 때와 같은 모양이라 Block을 12번 이어 쌓을 수 있다 |
| 출력층 점수 (Logit) | [1, 23, 50257] | 자리마다 사전 전체에 매긴 점수 |
| 마지막 자리 확률 | [50257] | 마지막 자리 점수만 Softmax로 바꾼 값. 합이 1이다 |

출력층 점수는 23개 자리 모두에서 나오지만, 다음 Token을 고를 때는 마지막 자리 'some'의 점수만 쓴다. 고른 Token은 입력 맨 끝에 붙고, 다음 계산에서는 입력이 [1, 24] 모양이 된다. 실습 4-3의 10 Token을 이어 쓰는 동안 입력은 23개에서 32개까지 하나씩 길어진다.

실습 4-3에서 이어 쓴 10 Token을 번호로 나타내면 22514, 13, 198, 198, 40, 481, 2822, 683, 617, 22514이다(출력 글자를 GPT-2 Tokenizer로 다시 번호로 바꾼 값). 13은 마침표, 198은 줄바꿈이다.

## 부록 C. 실습 5에서 쓴 설정

세 방식은 모두 transformers(공개 모델을 쓰게 해 주는 파이썬 도구)의 `generate` 함수에 이미 들어 있어서, 직접 구현하지 않고 옵션 값만 바꿔 골랐다. 실습에서 쓴 설정은 다음과 같다.

| 방식 | 설정 (generate 옵션) | 뜻 |
|---|---|---|
| 공통 | `max_new_tokens=12`, `temperature=1.0`, `torch.manual_seed(s)` (s = 0, 1, 2) | 12 Token까지 이어 쓰고, 확률은 그대로 쓰며, seed를 0·1·2로 고정해 세 번 돌린다 |
| Greedy | `do_sample=False` | 뽑지 않고 1위만 고른다. 결과가 같으므로 한 번만 돌렸다 |
| Top-K 50 | `do_sample=True, top_k=50, top_p=1.0` | 상위 50개 안에서 뽑는다. top_p=1.0은 Top-P를 끈다는 뜻이다 |
| Top-P 0.9 | `do_sample=True, top_k=0, top_p=0.9` | 누적 90%까지의 후보 안에서 뽑는다. top_k=0은 Top-K를 끈다는 뜻이다 |
| 전체에서 뽑기 | `do_sample=True, top_k=0, top_p=1.0` | 후보를 줄이지 않고 50,257개 전체에서 확률대로 뽑는다 |

transformers는 따로 지정하지 않으면 top_k를 50으로 두기 때문에, Top-P만 쓰려면 top_k=0으로 Top-K를 직접 꺼야 한다. 그렇지 않으면 두 방식이 함께 걸린다.

## 부록 D. 실행 화면

실행 화면을 그대로 옮겼다. `#`로 시작하는 줄은 설명을 위해 덧붙인 것이다.

### 실습 1. Tokenizer 비교

```text
문장: Minsu likes apples.
  GPT-2: 6개
    ID   : 44, 1040, 84, 7832, 22514, 13
    조각 : [M] [ins] [u] [ likes] [ apples] [.]
  GPT-4o: 5개
    ID   : 44, 137906, 18861, 57814, 13
    조각 : [M] [insu] [ likes] [ apples] [.]

문장: 인공지능을 공부한다
  GPT-2: 24개
    ID   : 35975, 116, 166, 111, 113, 168, 100, 222, 167, 232, 98, 35975, 226, 220, 166, 111, 113, 167, 114, 222, 47991, 250, 46695, 97
    조각 : [?] [?] [?] [?] [?] [?] [?] [?] [?] [?] [?] [?] [?] [ ] [?] [?] [?] [?] [?] [?] [?] [?] [?] [?]
  GPT-4o: 6개
    ID   : 5544, 185890, 19906, 3281, 179671, 29423
    조각 : [인] [공지] [능] [을] [ 공부] [한다]
```

ID는 그 조각이 Tokenizer 사전에서 몇 번째인지를 나타내는 번호이다. 사전이 다르면 같은 조각도 번호가 다르다. 예를 들어 [ apples]는 GPT-2에서 22514, GPT-4o에서 57814이다. GPT-2 화면의 [?]는 한글 한 글자가 바이트 2~3개로 쪼개져, 조각 하나만으로는 글자가 되지 않아 물음표로 찍힌 것이다.

### 실습 4-1. 다음 Token 확률과 Temperature

```text
1) 다음 Token 상위 5개
   ' apples' 16.6%, '.' 4.4%, ' apple' 3.0%, ' of' 2.9%, ' grapes' 2.5%
```

화면에서 따옴표 안의 글자가 Token 하나이다. ' apples'처럼 앞에 공백이 붙은 것은 공백까지 한 조각이기 때문이다.

```text
2) Temperature에 따른 변화
   T=0.5: ' apples' 80.3%, '.' 5.6%, ' apple' 2.7%
   T=1.0: ' apples' 16.6%, '.' 4.4%, ' apple' 3.0%
   T=2.0: ' apples' 0.7%, '.' 0.3%, ' apple' 0.3%
```

### 실습 4-2. Block을 지나며 답이 생긴다

```text
3) Block을 지날 때마다 마지막 자리에서 본 후보 확률
   Block  0 뒤: 1위 ' mathemat' | apples 0.00%, grapes 0.00%
   Block  1 뒤: 1위 ' very' | apples 0.00%, grapes 0.00%
   Block  2 뒤: 1위 'place' | apples 0.00%, grapes 0.00%
# Block 3~7 뒤 줄은 모두 1위 'place', apples 0.00%, grapes 0.00%라서 줄였다.
   Block  8 뒤: 1위 'place' | apples 0.00%, grapes 0.00%
   Block  9 뒤: 1위 'place' | apples 0.53%, grapes 0.11%
   Block 10 뒤: 1위 ' apples' | apples 19.38%, grapes 1.47%
   Block 11 뒤: 1위 ' apples' | apples 64.55%, grapes 4.85%
   Block 12 뒤: 1위 ',' | apples 0.00%, grapes 0.00%
# Block 12 줄은 코드 오류로 틀린 값이다(아래 설명). 표에는 최종 출력 값을 넣었다.
```

### 실습 4-3. 마지막 자리가 본 Token

```text
4) 마지막 Block에서 마지막 자리가 많이 본 Token (Head 평균, 상위 5개)
    0번 'M' 38.8%
   20번 ' buy' 7.6%
    4번 ' apples' 7.5%
   21번 ' him' 5.4%
    9번 ' grapes' 5.4%
```

화면의 '0번', '20번'은 부록 B의 자리 번호이다.

### 실습 5. Greedy, Top-K, Top-P 비교

```text
1) 첫 Token 후보가 몇 개 남나
   Top-K  1: 후보 1개, 남은 확률 합 16.6%
   Top-K  5: 후보 5개, 남은 확률 합 29.4%
   Top-K 50: 후보 50개, 남은 확률 합 55.4%
   Top-P 0.5: 후보 33개, 남은 확률 합 50.2%
   Top-P 0.9: 후보 1118개, 남은 확률 합 90.0%
```

```text
2) Top-K 5로 남긴 후보와 다시 나눈 확률
   ' apples' 16.6% -> 56.3%
   '.' 4.4% -> 14.9%
   ' apple' 3.0% -> 10.3%
   ' of' 2.9% -> 9.9%
   ' grapes' 2.5% -> 8.6%
```

```text
3) 방식별 이어 쓰기 (12 Token, seed 0부터 3번)
   [Greedy]
     1. ...some apples.\n\nI will buy him some apples. I
   [Top-K 50]
     1. ...some sweets when he wakes up.\n\nAfter the story,
     2. ...some apple juice. It's not just for Christmas but also for
     3. ...some apples and eat a few of them. He is excited.
   [Top-P 0.9]
     1. ...some along with seven more pretty Girls...<|endoftext|>
     2. ...some apple custard instead of ones.\n\n\nSomething else I
     3. ...some raisins and eat them each night. He loves singing
   [전체에서 뽑기]
# 세 줄 모두 Top-P 0.9와 같아서 줄였다.
```

화면의 \n은 줄바꿈 Token을 글자로 보이게 바꾼 것이다. 본문 표에는 읽기 쉽게 줄바꿈 뒤 내용을 줄였다.

### 실습 6. Head 144개가 보는 곳

```text
입력: Minsu likes apples and Jisu likes grapes. For Minsu's birthday, I will buy him some
Token 23개, Block 12개 x Head 12개 = Head 144개

1) 첫 Token에 몰린 비율 (Head 144개 평균, 자리 1 이후)
   56.2%
```

```text
2) 바로 앞 Token을 가장 많이 보는 Head 상위 5개 (자리 1 이후 평균)
   Block  5 Head 12: 바로 앞 Token에 100.0%
   Block  3 Head  3: 바로 앞 Token에 56.3%
   Block  4 Head  8: 바로 앞 Token에 43.2%
   Block  4 Head  3: 바로 앞 Token에 36.9%
   Block  3 Head 10: 바로 앞 Token에 35.5%
```

```text
3) 마지막 자리 'some'이 첫 Token을 빼고 가장 많이 본 Token, Head별
   [Block 12]
     Head  1: ' I' 11.6%
     Head  2: ' apples' 9.7%
     Head  3: ' grapes' 11.5%
     Head  4: ' buy' 8.5%
     Head  5: ' J' 13.1%
     Head  6: ' apples' 6.5%
     Head  7: ' apples' 9.7%
     Head  8: ' some' 6.7%
     Head  9: ' buy' 22.4%
     Head 10: ' grapes' 7.8%
     Head 11: ' apples' 23.6%
     Head 12: ' buy' 23.7%
# Block 1과 Block 6도 같은 형식으로 Head 12개씩 출력된다.
```

```text
4) 마지막 자리가 apples를 가장 많이 본 Head 상위 5개
   Block 11 Head  8: apples에 42.2%
   Block  9 Head  4: apples에 41.5%
   Block 11 Head  1: apples에 38.9%
   Block  9 Head 12: apples에 24.6%
   Block 12 Head 11: apples에 23.6%
```

### 실습 7. 최근 모델 Qwen2.5와 비교

```text
모델: Qwen/Qwen2.5-0.5B
가중치 494M개, Block 24개, 벡터 896칸, Head 14개, 사전 151,936개
Token 23개: [M] [ins] [u] [ likes] [ apples] [ and] [ J] [isu] [ likes] [ grapes] [.] [ For] [ M] [ins] [u] ['s] [ birthday] [,] [ I] [ will] [ buy] [ him] [ some]

1) 다음 Token 상위 5개
   ' apples' 42.6%, ' grapes' 24.6%, ' fruits' 8.1%, ' fruit' 5.7%, ' of' 2.9%
```

```text
3) Block을 지날 때마다 마지막 자리에서 본 후보 확률 (Logit Lens)
   Block 11개 지난 뒤: 1위 '겟' | apples 0.00%, grapes 0.01%
   Block 12개 지난 뒤: 1위 '鉴别' | apples 0.00%, grapes 0.00%
# Block 13~18 줄은 줄였다.
   Block 19개 지난 뒤: 1위 '日子' | apples 0.00%, grapes 0.00%
   Block 20개 지난 뒤: 1위 ' gifts' | apples 0.01%, grapes 0.00%
   Block 21개 지난 뒤: 1위 ' fruits' | apples 3.81%, grapes 0.93%
   Block 22개 지난 뒤: 1위 ' apples' | apples 31.30%, grapes 2.74%
   Block 23개 지난 뒤: 1위 ' apples' | apples 83.96%, grapes 1.34%
   Block 24개 지난 뒤: 1위 ' apples' | apples 42.63%, grapes 24.57%
```

### 7.2 실습 3. 다음 Token 예측 학습

```text
B: 직전 Token + 앞 Token 빈도 사용
수정 횟수 | 전체 학습 예시 Loss | '민수 는' 사과 | '민수 는' 포도
  0 | 2.1972 | 11.11% | 11.11%
 10 | 1.3112 | 24.16% | 19.14%
 50 | 0.4162 | 59.57% | 23.59%
200 | 0.2020 | 86.44% | 10.29%
500 | 0.1631 | 94.33% | 4.52%
```

## References

1. Vaswani et al., Attention Is All You Need, 2017. https://arxiv.org/abs/1706.03762
2. Radford et al., Language Models are Unsupervised Multitask Learners (GPT-2), 2019
3. Devlin et al., BERT, 2018. https://arxiv.org/abs/1810.04805
4. Brown et al., Language Models are Few-Shot Learners (GPT-3), 2020. https://arxiv.org/abs/2005.14165
5. Andrej Karpathy, build-nanogpt. https://github.com/karpathy/build-nanogpt
6. Xiao et al., Efficient Streaming Language Models with Attention Sinks, 2023. https://arxiv.org/abs/2309.17453
7. nostalgebraist, interpreting GPT: the logit lens, 2020. https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens
8. Xiong et al., On Layer Normalization in the Transformer Architecture, 2020. https://arxiv.org/abs/2002.04745
9. Liu et al., Understanding the Difficulty of Training Transformers, 2020. https://arxiv.org/abs/2004.08249
10. Shazeer, GLU Variants Improve Transformer, 2020. https://arxiv.org/abs/2002.05202
11. Su et al., RoFormer: Enhanced Transformer with Rotary Position Embedding, 2021. https://arxiv.org/abs/2104.09864
12. Ainslie et al., GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints, 2023. https://arxiv.org/abs/2305.13245
