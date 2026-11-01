# LLM은 어떻게 답을 고르나: Transformer 구조와 GPT-2로 들여다본 결과

ChatGPT 같은 LLM(Large Language Model, 대규모 언어 모델)이 하는 일은 하나다. 지금까지의 글을 보고 다음에 올 Token 하나를 고른다. 답이 끝날 때까지 이 일을 반복한다. 이 글은 그 과정을 구조 순서대로 짚는다. 그리고 공개 모델 GPT-2와 Qwen2.5에 같은 문장을 넣어 중간값을 꺼내 본 결과를 함께 정리했다.

> Token: 모델이 글을 처리하는 단위. 단어 하나일 수도 있고 글자 하나나 그보다 작은 조각일 수도 있다.

---

## 1. 실험에 쓴 문장

```text
민수는 사과를 좋아하고 지수는 포도를 좋아해. 민수 생일 선물로 뭘 살까?
```

질문에는 '사과'라는 말이 없다. 답하려면 앞 문장에서 민수와 사과를 이어야 한다. 이 연결이 모델 안 어디에서 생기는지가 이 글의 관심사이다.

GPT-2는 영어로 학습한 모델이라 같은 뜻의 영어 문장을 넣었다.

```text
Minsu likes apples and Jisu likes grapes. For Minsu's birthday, I will buy him some
```

모델은 Hugging Face에 공개된 원본 가중치를 그대로 받아 노트북 CPU로 돌렸다. 가중치를 고치거나 추가 학습하지 않았다. 결과는 출력된 값을 그대로 옮겼다. 같은 모델에 같은 문장을 넣으면 누가 돌려도 같은 값이 나온다.

> 가중치: 신경망 안에서 곱해지는 숫자. 처음엔 무작위 값이고 학습으로 정해진다.

---

## 2. 왜 Transformer인가

| 시기 | 컴퓨터가 글을 다룬 방식 | 한계 |
|---|---|---|
| 규칙 | 사람이 문법과 단어 사전을 직접 넣는다 | 예외가 끝이 없다 |
| 통계 | 어떤 단어 다음에 어떤 단어가 자주 오는지 센다 | 바로 앞 두세 단어만 본다 |
| RNN, LSTM | 신경망이 한 단어씩 읽으며 기억을 넘긴다 | 문장이 길면 앞 내용이 흐려진다. 차례로 읽어서 느리다 |
| Transformer (2017) | 모든 단어를 한꺼번에 놓고 서로 비교한다 | 단어끼리 모두 비교하므로 글이 길어지면 계산량이 길이의 제곱으로 늘어난다 |

> RNN(Recurrent Neural Network, 순환 신경망): 단어를 하나씩 읽으며 기억을 다음 칸에 넘기는 신경망. LSTM은 그 기억을 더 오래 유지하도록 고친 RNN이다.

![그림 1](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-02.png)

RNN은 귓속말 전달 게임과 비슷하다. 줄이 길면 처음 말이 흐려진다. 한 명씩 차례로 넘기니 느리기도 하다. Transformer는 모두가 한 방에 모여 필요한 사람에게 바로 묻는 방식이라 멀리 떨어진 단어도 한 번에 연결된다. 문장 전체를 동시에 계산하므로 GPU로 빠르게 돌릴 수 있었다. 덕분에 많은 글로 큰 모델을 학습할 수 있었다. 모델은 키울수록 성능이 올랐다. 그 결과가 GPT-3와 ChatGPT이다.

> GPU: 같은 계산을 수천 개 동시에 하는 칩.

Attention은 '주의, 주목'이라는 뜻이다. 위 문장에서 '살까'를 읽은 사람은 '민수'와 '사과'에 눈이 가고 '지수'와 '포도'는 덜 본다. Attention은 이 행동을 계산으로 옮긴 것이다. 단어마다 앞 단어 중 어디에 얼마나 주목할지 비율을 정한다. 그 비율만큼 정보를 가져온다. 논문 제목이 Attention Is All You Need인 것은 RNN이나 합성곱 없이 Attention으로 단어를 잇는 구조이기 때문이다. 다만 Block 안에는 Attention 말고도 FFN이라는 계산이 함께 들어 있다.

---

## 3. 전체 흐름과 구조

![그림 2](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-04.png)

| 단계 | 하는 일 | 예시에서 |
|---|---|---|
| ① 글을 숫자로 | 글을 Token으로 자르고 Token마다 숫자 벡터로 바꾼다 | '민수', '사과'가 벡터가 된다 |
| ② 문맥 모으기 | 각 Token이 앞쪽 Token의 정보를 모으고 가공한다. 여러 번 반복한다 | 마지막 자리에 민수가 사과를 좋아한다는 정보가 모인다 |
| ③ 다음 Token 고르기 | 후보 전체에 확률을 매기고 하나를 고른다 | '사과'가 1위 |
| ④ 반복 | 고른 Token을 붙여 ①부터 다시 한다 | 사과 → 를 → 추천해요 |

> 벡터: 숫자 여러 개를 한 줄로 묶은 값. 예: [0.9, 0.8, 0.1].

같은 흐름을 GPT-2(124M)의 부품으로 그리면 아래와 같다. 124M은 가중치가 1억 2,400만 개라는 뜻이다.

![그림 3](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-05.png)

| 부품 | 크기 (GPT-2) | 흐름에서 |
|---|---|---|
| Tokenizer 사전 | Token 50,257개 | ① |
| 벡터 한 개 | 숫자 768개 | ① |
| 한 번에 읽는 길이 | Token 1,024개 | ① |
| Transformer Block | 12개, Block마다 Head 12개 | ② |
| 출력층과 Softmax | 후보 50,257개 | ③ |

대형 LLM도 이 흐름은 같다. 사전, 벡터, Block 수가 커졌고, 위치 정보나 정규화 같은 내부 부품도 일부 바뀌었다. 이 차이는 뒤에서 따로 비교한다.

---

## 4. 단계별로 실제 결과 보기

### 4.1 Tokenization: 글을 조각내고 번호를 붙인다

GPT-2와 GPT-4o의 실제 Tokenizer에 같은 문장을 넣었다.

| 문장 | GPT-2 | GPT-4o |
|---|---|---|
| 민수는 사과를 좋아해. | 26개 | 9개: [민] [수] [는] [ 사] [과] [를] [ 좋아] [해] [.] |
| Minsu likes apples. | 6개: [M] [ins] [u] [ likes] [ apples] [.] | 5개: [M] [insu] [ likes] [ apples] [.] |
| 인공지능을 공부한다 | 24개 | 6개: [인] [공지] [능] [을] [ 공부] [한다] |

GPT-2는 영어 위주로 사전을 만들어서 한글 한 글자가 바이트 단위로 2~3개씩 쪼개진다. GPT-4o는 사전이 커서 한글도 글자나 단어 단위로 자른다. 같은 내용이라도 언어에 따라 Token 수가 다르다. 그만큼 비용과 속도도 달라진다.

GPT-4o가 '인공지능'을 [인] [공지] [능]으로 자른 것도 눈여겨볼 만하다. 사람이 생각하는 단어 경계와 다르다. Tokenizer가 쓰는 BPE(Byte Pair Encoding)는 뜻이 아니라 학습 데이터에서 함께 나온 횟수로 조각을 합치기 때문이다.

### 4.2 Embedding과 위치: 번호를 벡터로 바꾸고 자리를 더한다

Token 번호 자체에는 뜻이 없다. 모델은 번호로 Embedding 표에서 숫자 768개짜리 벡터를 꺼낸다. 여기에 몇 번째 자리인지를 더한다. 학습을 거치면 비슷하게 쓰이는 Token끼리 벡터가 가까워진다.

위치를 따로 넣는 이유는 Attention이 문장을 한꺼번에 보기 때문이다. 위치 정보가 없으면 '민수가 지수를 좋아해'와 '지수가 민수를 좋아해'를 구분하지 못한다. 위치를 넣는 방식은 모델마다 다르다.

| 방식 | 위치 값 | 쓰는 모델 |
|---|---|---|
| 사인·코사인 | 공식으로 계산한다. 학습하지 않는다 | 논문의 Transformer |
| 위치 표 학습 | 1,024줄 표를 학습한다. 그보다 긴 글은 받지 못한다 | GPT-2 |
| RoPE | 더하지 않고 Attention 안에서 벡터를 자리만큼 회전한다. Token 사이 거리가 회전 각도로 들어가 긴 글로 늘리기 쉽다 | Llama, Qwen 등 최근 모델 대부분 |

### 4.3 Self-Attention: 앞쪽 Token에서 정보를 가져온다

![그림 4](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-10.png)

각 Token은 Query(찾는 것), Key(내가 가진 것), Value(넘겨줄 정보)를 만든다. Query와 Key로 점수를 매기고 비율로 바꾼 뒤, 그 비율만큼 Value를 섞어 가져온다. 이때 뒤쪽 Token은 가린다(Mask). 학습할 때 정답 문장을 통째로 넣는데, 뒤를 볼 수 있으면 예측하지 않고 답을 베끼기 때문이다.

실제 GPT-2의 마지막 Block에서 마지막 자리 'some'이 앞쪽 Token에 준 비율을 꺼냈다(Head 12개 평균).

| Token | M (첫 Token) | buy | apples | him | grapes |
|---|---|---|---|---|---|
| 비율 | 38.8% | 7.6% | 7.5% | 5.4% | 5.4% |

M은 Minsu가 [M] [ins] [u]로 잘리면서 생긴 첫 조각이다. 38.8%가 몰린 것은 글자 뜻 때문이 아니라 첫 자리이기 때문이다. GPT 계열 모델은 볼 곳이 마땅치 않을 때 남는 비율을 첫 Token에 몰아 두는데, 이를 Attention Sink라고 부른다. Head 144개 전체 평균으로 봐도 비율의 56.2%가 첫 Token으로 갔다. 첫 Token을 빼면 사는 행동(buy), 두 과일(apples, grapes), 받는 사람(him)을 많이 봤다.

### 4.4 Block 반복: 답은 여러 층을 지나며 생긴다

![그림 5](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-16.png)

Attention과 FFN(Feed Forward Network)을 묶은 것이 Transformer Block이다. Attention이 재료를 모으면 FFN이 Token마다 따로 가공한다. 계산 결과는 원래 벡터에 덮어쓰지 않고 더한다(Residual Connection). 계산 앞에서는 값의 크기를 맞춘다(Layer Normalization). 둘 다 Block을 깊게 쌓아도 학습이 무너지지 않게 하는 장치이다.

'선물'에서 '민수'로, '민수가 좋아하는 것'으로, 다시 '사과'로 넘어가는 연결은 정보를 여러 번 이어 받아야 완성된다. 정말 그런지 보려고 Block 하나를 지날 때마다 마지막 자리 벡터를 출력층에 바로 넣어 보았다. '이 시점에서 답을 고르라면 무엇을 고를까'를 보는 방법으로, Logit Lens라고 부른다. 중간 벡터는 원래 출력층에 넣으라고 만든 값이 아니므로 대략적인 참고값이다.

| 지난 Block 수 | 그 시점의 1위 | apples | grapes |
|---|---|---|---|
| 0 (Embedding만) | mathemat | 0.00% | 0.00% |
| 2~8 | place | 0.00% | 0.00% |
| 9 | place | 0.53% | 0.11% |
| 10 | apples | 19.38% | 1.47% |
| 11 | apples | 64.55% | 4.85% |
| 12 (최종 출력) | apples | 16.6% | 2.5% |

![그림 6](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-25.png)

9번째 Block까지는 1위가 place 같은 엉뚱한 단어이고 apples는 0%에 가깝다. 10번째 Block을 지나서야 apples가 처음 1위로 올라선다. 답은 처음부터 있던 것이 아니라 Block을 여러 번 지난 뒤에 나타났다. apples를 가장 많이 보는 Head도 Block 9와 11에 몰려 있었다(Block 11 Head 8이 42.2%). 다만 이 Head들이 apples를 1위로 만든 원인인지는 이 실험으로 알 수 없다. 시점이 겹친다는 것까지만 말할 수 있다.

### 4.5 확률과 Sampling: 후보 중 하나를 고른다

마지막 자리의 벡터를 출력층에 넣으면 사전 50,257개 Token마다 점수(Logit)가 나온다. Softmax가 이 점수를 합이 100%인 확률로 바꾼다.

| 순위 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 다음 Token | apples | . | apple | of | grapes |
| 확률 | 16.6% | 4.4% | 3.0% | 2.9% | 2.5% |

GPT-2는 민수가 좋아하는 apples를 1위로, 지수가 좋아하는 grapes를 5위로 놓았다. 1위가 16.6%에 그친 것은 some 뒤에 올 수 있는 말이 5만 개 후보 안에 많기 때문이다.

Temperature는 확률을 얼마나 한쪽으로 몰지 정하는 값이다. 점수를 이 값으로 나눈 뒤 Softmax에 넣는다.

| Temperature | 0.5 | 1.0 | 2.0 |
|---|---|---|---|
| apples 확률 | 80.3% | 16.6% | 0.7% |

순위는 그대로이고 쏠림만 달라진다. 낮추면 1위로 몰린다. 높이면 5만 개 후보로 퍼져 답이 다양해진다.

이제 하나를 고를 차례이다. 방식은 세 가지가 널리 쓰인다.

| 방식 | 한 줄 설명 | 첫 Token에서 남은 후보 |
|---|---|---|
| Greedy | 매번 확률 1위만 고른다. 항상 같은 결과가 나온다 | 1개 (확률 합 16.6%) |
| Top-K 50 | 상위 50개만 남기고 그 안에서 확률대로 뽑는다 | 50개 (55.4%) |
| Top-P 0.9 | 확률을 높은 순으로 더해 90%가 될 때까지의 후보만 남긴다 | 1,118개 (90.0%) |

같은 문장을 방식마다 12 Token씩 이어 썼다. 뽑기 결과가 재현되도록 seed(무작위 수의 시작 번호)를 0, 1, 2로 고정해 한 번씩 돌렸다.

| 방식 | 이어 쓴 결과 (... buy him some 다음) |
|---|---|
| Greedy | apples. / I will buy him some apples. I |
| Top-K 50 | ① sweets when he wakes up. ② apple juice. It's not just for Christmas ③ apples and eat a few of them. He is excited. |
| Top-P 0.9 | ① along with seven more pretty Girls... [EOS] ② apple custard instead of ones. ③ raisins and eat them each night. |

> EOS(End Of Sequence): '문장이 끝났다'는 뜻의 특수 Token. 이 Token이 뽑히면 생성을 멈춘다.

Greedy는 몇 번을 돌려도 같았다. 문장을 끝낸 뒤에는 앞 문장을 되풀이했다. Top-K 50은 매번 다른 문장이 나오면서도 셋 다 살 물건으로 이어졌다. Top-P 0.9는 이 문장에서 후보가 1,118개나 남아 확률 낮은 Token도 뽑혔다. 그래서 문맥에서 먼 문장(①)이 나왔다. 같은 질문에 매번 조금씩 다른 답이 나오는 이유가 이 단계에 있다.

---

## 5. 논문 구조와 실제 모델의 차이

GPT는 2017년 논문의 Encoder와 Decoder 중 Decoder만 쓴다. 질문과 답을 한 줄로 이어 붙여 넣으므로 원문을 따로 읽을 Encoder가 필요 없다. 다음 Token 맞히기 하나로 번역, 요약, 대화를 모두 처리하게 되면서 과제마다 모델을 따로 만들 필요도 없어졌다. ChatGPT, Llama, Qwen 모두 이 갈래이다.

| 항목 | 논문 Transformer | GPT-2 (124M) | Llama 3 8B |
|---|---|---|---|
| 구조 | Encoder 6층 + Decoder 6층 | Decoder만 12층 | Decoder만 32층 |
| 벡터 칸 수 | 512 | 768 | 4,096 |
| 사전 크기 | 37,000 | 50,257 | 128,256 |
| 위치 정보 | 사인·코사인 공식 | 위치 표 학습 | RoPE (회전) |
| FFN 활성화 함수 | ReLU | GELU | SwiGLU |
| 정규화 위치 | 계산 뒤 | 계산 앞 | 계산 앞 (RMSNorm) |
| Key·Value | Head마다 따로 | Head마다 따로 | Head 4개가 한 벌을 나눠 씀 (GQA) |

![그림 7](https://raw.githubusercontent.com/WontelliJ/jw-velog/main/drafts/llm-transformer/images/fig-14.png)

차이마다 뜻하는 바는 다음과 같다.

- 정규화 위치: 계산 앞에서 맞추면 원래 값이 마지막 Block까지 그대로 이어져 층을 깊게 쌓아도 학습이 안정된다. GPT-2 이후 대부분의 LLM이 이 방식을 쓴다.
- RoPE: 위치 표는 길이가 정해져 있다. RoPE는 Token 사이 거리를 각도로 넣어 더 긴 글로 늘리기 쉽다.
- GQA: 답을 만들 때 앞 Token의 Key·Value를 저장해 두는데, Head 여럿이 한 벌을 나눠 쓰면 저장 공간이 줄어 빨라진다.
- 활성화 함수: 실험에서 성능이 조금 더 좋아서 바뀐 것이다. 이유가 분명히 밝혀진 것은 아니다.

뼈대는 같고 부품이 바뀌었다. 그래서 GPT-2로 본 동작 원리는 최근 모델에도 적용된다. 다만 확률이나 Head 번호 같은 숫자는 GPT-2에서만 나온 값이다.

---

## 6. 최근 모델 Qwen2.5로 다시 해 보기

같은 실험을 2024년 공개 모델 Qwen2.5-0.5B로 반복했다. RoPE, RMSNorm, SwiGLU, GQA를 쓰는 모델이다.

| | GPT-2 (2019) | Qwen2.5-0.5B (2024) |
|---|---|---|
| 가중치 | 1억 2,400만 개 | 4억 9,400만 개 |
| Block 수 | 12 | 24 |
| 다음 Token 1위 | apples 16.6% | apples 42.6% |
| grapes | 2.5% (5위) | 24.6% (2위) |
| 상위 5개 | apples, ., apple, of, grapes | apples, grapes, fruits, fruit, of |
| apples가 1위가 된 시점 | 12개 중 10번째 Block | 24개 중 22번째 Block |

Qwen2.5는 상위 5개 중 4개가 과일이다. 선물로 과일을 산다는 문맥을 GPT-2보다 확실히 잡았다. 그런데 grapes도 24.6%로 높다. apples와 grapes의 비율로 보면 GPT-2는 6.6배, Qwen2.5는 1.7배로 갈렸다. 큰 모델이 모든 면에서 나은 것은 아니다.

Block별 기록에서는 흥미로운 순서가 보였다. 20번째 Block에서 1위가 gifts(선물), 21번째에서 fruits(과일), 22번째에서 apples(사과)로 바뀌었다. 선물에서 과일로, 과일에서 사과로 좁혀 가는 연결이 실제 모델 안에서 그대로 드러난 것이다.

---

## 7. 학습: 다음 Token 맞히기를 반복한다

예전에는 사람이 정답을 붙인 데이터로 과제마다 따로 학습했다. GPT 계열은 글 자체에서 다음 단어를 정답으로 삼는다. 덕분에 정답지를 사람이 만들 필요가 줄었다. 인터넷의 글을 그대로 학습에 쓸 수 있게 되면서 쓸 수 있는 데이터도 크게 늘었다. 학습은 다음 Token을 맞히게 하고, 틀린 정도(Loss)가 줄어드는 쪽으로 가중치를 고치는 일을 반복하는 것이다.

이를 직접 보려고 문장 4개로 아주 작은 모델 두 개를 학습했다. Transformer는 아니지만 학습 방식은 LLM과 같다. 모델 A는 바로 앞 Token 하나만 보고, 모델 B는 앞에 나온 Token을 모두 본다.

```text
민수 는 사과 를 좋아해 .     지수 는 포도 를 좋아해 .
민수 는 사과 를 샀다 .       지수 는 포도 를 샀다 .
```

| 학습 횟수 | 0 | 10 | 50 | 200 | 500 |
|---|---|---|---|---|---|
| 모델 B Loss | 2.20 | 1.31 | 0.42 | 0.20 | 0.16 |
| 모델 B '민수 는 ___' 사과 / 포도 | 11% / 11% | 24% / 19% | 60% / 24% | 86% / 10% | 94% / 5% |
| 모델 A '민수 는 ___' 사과 / 포도 | 11% / 11% | 21% / 21% | 40% / 40% | 48% / 48% | 49% / 49% |

Loss가 줄어든다는 것은 정답 Token의 확률이 올라간다는 뜻이다. 모델 B는 학습할수록 '민수 는' 다음에 사과 쪽으로 기울어 94%까지 갔다. 모델 A는 사과와 포도가 함께 오르다 49%에서 멈췄다. 바로 앞의 '는'만 보니 민수인지 지수인지 알 수 없기 때문이다. 학습을 아무리 해도 입력에 구분할 정보가 없으면 구분하지 못한다. 앞쪽 정보를 가져오는 장치가 왜 필요한지 보여 주는 결과이다. Transformer에서는 이 일을 Self-Attention이 맡는다.

---

## 정리

| 단계 | 하는 일 | 실제로 본 것 |
|---|---|---|
| Tokenization | 문장을 조각내고 번호를 붙인다 | 같은 한국어 문장이 GPT-2는 26개, GPT-4o는 9개 |
| Embedding과 위치 | 번호를 벡터로 바꾸고 자리를 더한다 | GPT-2는 위치 표, 최근 모델은 RoPE |
| Self-Attention | 앞쪽 Token에서 관련 정보를 가져온다 | 마지막 자리가 buy, apples, him을 많이 봄. 첫 Token에 Attention Sink |
| Block 반복 | 가져온 정보를 가공하고 여러 번 반복한다 | GPT-2는 10번째 Block에서, Qwen2.5는 22번째에서 apples가 1위 |
| 확률과 Sampling | 후보에 확률을 매기고 하나를 고른다 | apples 16.6%로 1위. 고르는 방식에 따라 문장이 달라짐 |
| 학습 | 다음 Token을 맞히며 가중치를 고친다 | Loss 2.20에서 0.16으로, 사과 확률 11%에서 94%로 |

Transformer는 문장 전체를 한꺼번에 계산하는 구조로 모델을 크게 키울 수 있게 했다. LLM은 그 위에서 다음 Token 하나를 고르는 계산을 반복해 답을 만든다. 실제 모델을 들여다보니 답은 처음부터 정해져 있지 않았다. 여러 Block을 지나며 문맥이 쌓인 뒤에야 나타났다.

직접 해 보고 싶다면 아래 도구가 편하다.

- Transformer Explainer (poloclub.github.io/transformer-explainer): 브라우저에서 GPT-2에 문장을 넣고 Attention 비율과 Temperature 효과를 본다.
- Tiktokenizer (tiktokenizer.vercel.app): 여러 모델의 Tokenizer로 문장을 잘라 본다.
- build-nanogpt (github.com/karpathy/build-nanogpt): GPT-2를 코드로 처음부터 만들어 학습한다.

## References

1. Vaswani et al., Attention Is All You Need, 2017. https://arxiv.org/abs/1706.03762
2. Radford et al., Language Models are Unsupervised Multitask Learners (GPT-2), 2019
3. Brown et al., Language Models are Few-Shot Learners (GPT-3), 2020. https://arxiv.org/abs/2005.14165
4. Xiao et al., Efficient Streaming Language Models with Attention Sinks, 2023. https://arxiv.org/abs/2309.17453
5. nostalgebraist, interpreting GPT: the logit lens, 2020. https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens
6. Xiong et al., On Layer Normalization in the Transformer Architecture, 2020. https://arxiv.org/abs/2002.04745
7. Su et al., RoFormer: Enhanced Transformer with Rotary Position Embedding, 2021. https://arxiv.org/abs/2104.09864
8. Ainslie et al., GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints, 2023. https://arxiv.org/abs/2305.13245
