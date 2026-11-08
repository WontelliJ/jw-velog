<h1 id="llm은-어떻게-답을-만들까-2편-안쪽-들여다보기">LLM은 어떻게 답을 만들까 (2편: 안쪽 들여다보기)</h1>
<p>1편에서는 LLM이 다음 Token 하나를 고르기까지 6단계를 따라갔다. 마지막에 GPT-2는 질문에 없던 apples를 16.6%로 1위에 올렸다. 그런데 이 답이 모델 안 어디에서 생겼는지는 보지 않았다.</p>
<p>이번 글은 그 안쪽을 본다. 1편과 같은 문장을 GPT-2에 넣고 Block 하나, Head 하나 단위로 꺼내 보았다. 그다음 2024년 모델 Qwen2.5에 같은 문장을 넣어 비교했다. 마지막으로 아주 작은 모델을 직접 학습시키면서 확률이 어떻게 움직이는지 기록했다.</p>
<pre><code>입력: Minsu likes apples and Jisu likes grapes.
      For Minsu's birthday, I will buy him some</code></pre><p>숫자는 모두 Windows PC의 CPU로 GPT-2(124M)와 Qwen2.5-0.5B를 직접 돌린 결과이다.</p>
<h2 id="1-apples는-몇-번째-block에서-1위가-되나">1. apples는 몇 번째 Block에서 1위가 되나</h2>
<blockquote>
<p>GPT-2에서 apples는 12개 Block 중 10번째를 지나서야 처음 1위가 된다.</p>
</blockquote>
<p>1편에서 '민수'와 '사과'를 잇는 연결은 Block을 여러 번 지나야 완성된다고 했다. 정말 그런지 보려면 Block 중간에서 답을 꺼내 보면 된다.</p>
<p>그래서 Block 하나를 지날 때마다 마지막 자리('some')의 벡터를 출력층에 바로 넣었다. 이렇게 하면 '이 시점에서 답을 고르라고 하면 무엇을 고를까'를 볼 수 있다.</p>
<p><sub>Logit Lens: 계산 중간의 벡터를 출력층에 바로 넣어 그 시점의 예측을 보는 방법</sub></p>
<table>
<thead>
<tr>
<th>지난 Block 수</th>
<th>그 시점의 1위</th>
<th>apples</th>
<th>grapes</th>
</tr>
</thead>
<tbody><tr>
<td>0 (Embedding만)</td>
<td>mathemat</td>
<td>0.00%</td>
<td>0.00%</td>
</tr>
<tr>
<td>1</td>
<td>very</td>
<td>0.00%</td>
<td>0.00%</td>
</tr>
<tr>
<td>2~8</td>
<td>place</td>
<td>0.00%</td>
<td>0.00%</td>
</tr>
<tr>
<td>9</td>
<td>place</td>
<td>0.53%</td>
<td>0.11%</td>
</tr>
<tr>
<td>10</td>
<td>apples</td>
<td>19.38%</td>
<td>1.47%</td>
</tr>
<tr>
<td>11</td>
<td>apples</td>
<td>64.55%</td>
<td>4.85%</td>
</tr>
<tr>
<td>12 (최종 출력)</td>
<td>apples</td>
<td>16.6%</td>
<td>2.5%</td>
</tr>
</tbody></table>
<p>앞쪽 9개 Block을 지나는 동안 1위는 place 같은 엉뚱한 단어이고 apples는 0%에 가깝다. 이 구간에서 모델이 정확히 무엇을 하는지는 이 방법으로 알 수 없다. 앞 단어들의 정보를 모으는 중이라고 짐작할 뿐이다.</p>
<p>10번째 Block을 지나자 apples가 19.38%로 처음 1위가 된다. 11번째에서는 64.55%까지 오른다. 답이 처음부터 들어 있던 것이 아니라 Block을 거치면서 만들어졌다.</p>
<p>이상한 점도 하나 있다. 마지막 Block을 지나면서 apples가 64.55%에서 16.6%로 떨어진다. 1위는 지켰지만 확신은 크게 줄었다. 뒤에서 볼 Qwen2.5에서도 마지막 Block에서 확률이 내려갔다. 왜 그런지는 이번 실험만으로는 알 수 없었다.</p>
<p>처음 돌렸을 때는 Block 12 줄에 1위 ',' / apples 0.00%가 찍혀서 한참 헤맸다. 최종 출력과 같아야 하는 값이 전혀 달랐다. 원인은 코드에서 정규화를 두 번 한 것이었다. transformers가 돌려주는 마지막 hidden state에는 이미 정규화가 되어 있는데, 그 위에 한 번 더 적용했다. 고친 뒤에는 최종 출력과 같은 값이 나온다.</p>
<p>중간 벡터는 원래 출력층에 넣으라고 만든 값이 아니다. 그래서 위 표의 중간 숫자는 대략적인 참고값으로 봐야 한다.</p>
<h2 id="2-첫-token에-몰리는-비율-attention-sink">2. 첫 Token에 몰리는 비율, Attention Sink</h2>
<blockquote>
<p>마지막 자리는 Attention의 38.8%를 문장 첫 조각 'M'에 준다. 뜻 때문이 아니라 첫 자리라서 생기는 현상이다.</p>
</blockquote>
<p>1편에서 'some'이 많이 본 Token을 보여 줄 때 괄호로 넘긴 숫자가 있다. 첫 Token에 38.8%가 몰렸다는 것이다.</p>
<table>
<thead>
<tr>
<th>Token</th>
<th>M (첫 Token)</th>
<th>buy</th>
<th>apples</th>
<th>him</th>
<th>grapes</th>
</tr>
</thead>
<tbody><tr>
<td>비율</td>
<td>38.8%</td>
<td>7.6%</td>
<td>7.5%</td>
<td>5.4%</td>
<td>5.4%</td>
</tr>
</tbody></table>
<p>M은 'Minsu'가 [M] [ins] [u]로 잘리면서 생긴 첫 조각이다. 이 조각이 선물을 고르는 데 중요할 리는 없다.</p>
<p>마지막 Block만 이런지 궁금해서 Head 144개(Block 12개 × Head 12개)를 모두 평균 내 보았다. 각 자리가 첫 Token에 주는 비율은 평균 56.2%였다. 모델 전체에서 절반이 넘는 비율이 첫 자리로 간다.</p>
<p><sub>Head: Attention을 여러 갈래로 나눠 따로 계산하는 단위. GPT-2는 Block마다 12개가 있다<br />
Attention Sink: 특별히 볼 곳이 없을 때 남는 Attention 비율이 첫 Token에 모이는 현상</sub></p>
<p>Attention 비율은 Softmax를 거치기 때문에 합이 항상 100%이다. 볼 곳이 마땅치 않아도 어딘가에는 나눠 줘야 한다. GPT 계열 모델은 이 남는 몫을 첫 Token에 몰아 두는 것으로 알려져 있다. 그래서 Attention 비율을 해석할 때는 첫 Token을 빼고 보는 편이 맞다.</p>
<h2 id="3-head마다-보는-곳이-다르다">3. Head마다 보는 곳이 다르다</h2>
<blockquote>
<p>같은 문장을 보면서도 Head 144개는 저마다 다른 곳을 본다.</p>
</blockquote>
<p>첫 Token을 빼고 나면 Head마다 성격이 꽤 갈린다. 바로 앞 Token만 보는 Head가 가장 눈에 띄었다.</p>
<table>
<thead>
<tr>
<th>Head</th>
<th>바로 앞 Token에 준 비율 (평균)</th>
</tr>
</thead>
<tbody><tr>
<td>Block 5 Head 12</td>
<td>100.0%</td>
</tr>
<tr>
<td>Block 3 Head 3</td>
<td>56.3%</td>
</tr>
<tr>
<td>Block 4 Head 8</td>
<td>43.2%</td>
</tr>
</tbody></table>
<p>Block 5의 Head 12는 어느 자리에서든 바로 앞 Token에 100%를 준다. 하는 일이 하나로 정해져 있다. 1편 3단계에서 Attention은 따로 알려 주지 않으면 순서를 모른다고 했는데, 이런 Head가 바로 앞이 무엇이었는지를 옮겨 주는 것으로 보인다.</p>
<p>마지막 자리 'some'이 첫 Token을 빼고 가장 많이 본 Token을 Block별로 세어 보면 층마다 관심사가 바뀐다.</p>
<table>
<thead>
<tr>
<th>Block</th>
<th>가장 많이 본 Token (Head 12개 기준)</th>
</tr>
</thead>
<tbody><tr>
<td>1</td>
<td>some 자기 자신 6개. 나머지는 For, ., apples, 쉼표, I, likes가 하나씩</td>
</tr>
<tr>
<td>6</td>
<td>him 4개, buy 2개, . 2개, apples 1개 등</td>
</tr>
<tr>
<td>12</td>
<td>apples 4개, buy 3개, grapes 2개 등</td>
</tr>
</tbody></table>
<p>앞쪽 Block은 대부분 자기 자신을 본다. 중간 Block은 받는 사람(him)과 행동(buy)을 보고, 마지막 Block은 과일(apples, grapes)과 buy를 본다.</p>
<p>apples를 가장 많이 본 Head도 찾아보았다.</p>
<table>
<thead>
<tr>
<th>Head</th>
<th>apples에 준 비율</th>
</tr>
</thead>
<tbody><tr>
<td>Block 11 Head 8</td>
<td>42.2%</td>
</tr>
<tr>
<td>Block 9 Head 4</td>
<td>41.5%</td>
</tr>
<tr>
<td>Block 11 Head 1</td>
<td>38.9%</td>
</tr>
</tbody></table>
<p>이 Head들은 Block 9와 11에 몰려 있다. 1번 실험에서 apples가 1위로 올라선 시점(Block 10)과 가깝다. 다만 이 Head들이 apples를 1위로 만든 원인인지는 이 실험으로 알 수 없다. 시점이 겹친다는 것까지만 말할 수 있다.</p>
<h2 id="4-2017년-논문-gpt-2-최근-모델은-무엇이-다른가">4. 2017년 논문, GPT-2, 최근 모델은 무엇이 다른가</h2>
<blockquote>
<p>뼈대는 그대로이고 크기와 부품이 바뀌었다.</p>
</blockquote>
<p>Transformer 논문은 원래 번역용이었다. 원문을 읽는 Encoder와 번역문을 쓰는 Decoder가 따로 있다. GPT는 여기서 Decoder만 떼어 냈다. 질문과 답을 한 줄로 이어 붙여 넣기 때문에 원문을 따로 읽을 Encoder가 필요 없다. ChatGPT, Llama, Qwen 모두 이 갈래에 속한다.</p>
<p><sub>Encoder: 문장을 읽어 숫자에 담는 부분<br />
Decoder: 숫자에서 문장을 한 단어씩 꺼내는 부분</sub></p>
<p>아래 값은 각 논문과 공개 설정을 기준으로 정리했다.</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>논문 Transformer (2017, base)</th>
<th>GPT-2 124M (2019)</th>
<th>Llama 3 8B (2024)</th>
</tr>
</thead>
<tbody><tr>
<td>구조</td>
<td>Encoder 6층 + Decoder 6층</td>
<td>Decoder만 12층</td>
<td>Decoder만 32층</td>
</tr>
<tr>
<td>벡터 칸 수</td>
<td>512</td>
<td>768</td>
<td>4,096</td>
</tr>
<tr>
<td>Head 수</td>
<td>8</td>
<td>12</td>
<td>32 (Key·Value는 8개를 나눠 씀)</td>
</tr>
<tr>
<td>사전 크기</td>
<td>37,000</td>
<td>50,257</td>
<td>128,256</td>
</tr>
<tr>
<td>위치 정보</td>
<td>사인·코사인 공식</td>
<td>위치 표를 학습 (1,024줄)</td>
<td>RoPE (회전)</td>
</tr>
<tr>
<td>FFN 활성화 함수</td>
<td>ReLU</td>
<td>GELU</td>
<td>SwiGLU</td>
</tr>
<tr>
<td>정규화 위치</td>
<td>계산 뒤</td>
<td>계산 앞</td>
<td>계산 앞 (RMSNorm)</td>
</tr>
</tbody></table>
<p><sub>정규화: 벡터 값의 크기를 일정하게 맞추는 계산<br />
활성화 함수: FFN 안에서 값을 그대로 넘길지 줄일지 정하는 함수</sub></p>
<p>표의 차이는 대부분 크기를 키우고 부품을 바꾼 것이다. 그중 1편에서 미뤄 둔 위치 정보와 이유가 가장 분명한 정규화 위치만 짧게 본다.</p>
<h3 id="위치-정보">위치 정보</h3>
<p>논문은 자리마다 사인·코사인 공식으로 값을 계산해 더했다. GPT-2는 공식 대신 1,024줄짜리 위치 표를 학습했다. 표가 1,024줄이라서 GPT-2는 한 번에 Token 1,024개까지만 받는다.</p>
<p>최근 모델이 쓰는 RoPE는 값을 더하지 않는다. 자리에 따라 벡터를 정해진 각도만큼 돌린다. 두 Token의 각도 차이가 곧 거리라서 Attention 점수를 계산할 때 '몇 칸 떨어져 있나'가 자연스럽게 들어간다.</p>
<h3 id="정규화-위치">정규화 위치</h3>
<p>논문은 Attention을 계산하고 원래 값을 더한 뒤에 크기를 맞췄다. GPT-2는 순서를 바꿔 크기를 먼저 맞추고 계산한 다음 원래 값을 더한다.</p>
<pre><code>논문   : 입력 → Attention → 입력 더하기 → 정규화
GPT-2  : 입력 → 정규화 → Attention → 입력 더하기</code></pre><p>GPT-2 방식에서는 원래 값이 정규화를 거치지 않고 다음 Block까지 그대로 이어진다. 그래서 층을 깊게 쌓아도 학습이 잘 무너지지 않는다. GPT-2 이후 대부분의 LLM이 이 순서를 쓴다.</p>
<p>부품은 바뀌었어도 Decoder만 쓰고, 앞쪽만 보는 Attention과 FFN을 Block으로 쌓는다는 점은 같다. 그래서 GPT-2로 확인한 동작은 최근 모델에도 그대로 적용된다. 다만 확률이나 Head 번호 같은 숫자는 GPT-2에서만 나온 값이다.</p>
<h2 id="5-같은-문장을-qwen25에-넣으면">5. 같은 문장을 Qwen2.5에 넣으면</h2>
<blockquote>
<p>최근 모델도 Block을 지나며 '선물 → 과일 → 사과' 순서로 답을 좁혀 간다.</p>
</blockquote>
<p>2024년에 나온 작은 공개 모델 Qwen2.5-0.5B로 1번 실험을 똑같이 해 보았다. Qwen2.5는 위 표의 최근 부품(RoPE, RMSNorm, SwiGLU)을 쓰는 모델이다.</p>
<table>
<thead>
<tr>
<th></th>
<th>GPT-2 (2019)</th>
<th>Qwen2.5-0.5B (2024)</th>
</tr>
</thead>
<tbody><tr>
<td>가중치</td>
<td>1억 2,400만 개</td>
<td>4억 9,400만 개</td>
</tr>
<tr>
<td>Block 수</td>
<td>12</td>
<td>24</td>
</tr>
<tr>
<td>사전 크기</td>
<td>50,257</td>
<td>151,936</td>
</tr>
<tr>
<td>예시 문장 Token 수</td>
<td>23개</td>
<td>23개 (같은 조각)</td>
</tr>
<tr>
<td>다음 Token 1위</td>
<td>apples 16.6%</td>
<td>apples 42.6%</td>
</tr>
<tr>
<td>grapes</td>
<td>2.5% (5위)</td>
<td>24.6% (2위)</td>
</tr>
<tr>
<td>상위 5개</td>
<td>apples, ., apple, of, grapes</td>
<td>apples, grapes, fruits, fruit, of</td>
</tr>
</tbody></table>
<p>Qwen2.5는 상위 5개 중 4개가 과일이다. 선물로 과일을 산다는 문맥은 GPT-2보다 확실히 잡았다.</p>
<p>그런데 grapes도 24.6%로 높다. apples가 grapes보다 몇 배 높은지 보면 GPT-2는 6.6배, Qwen2.5는 1.7배이다. 민수가 좋아하는 것과 지수가 좋아하는 것을 가르는 일은 오히려 GPT-2가 더 분명했다. 모델이 크다고 모든 면에서 나은 것은 아니었다.</p>
<p>Block별 기록은 이렇게 나왔다.</p>
<table>
<thead>
<tr>
<th>지난 Block 수</th>
<th>그 시점의 1위</th>
<th>apples</th>
<th>grapes</th>
</tr>
</thead>
<tbody><tr>
<td>0~19</td>
<td>some, 日子 등 뜻 없는 Token</td>
<td>0.01% 이하</td>
<td>0.05% 이하</td>
</tr>
<tr>
<td>20</td>
<td>gifts</td>
<td>0.01%</td>
<td>0.00%</td>
</tr>
<tr>
<td>21</td>
<td>fruits</td>
<td>3.81%</td>
<td>0.93%</td>
</tr>
<tr>
<td>22</td>
<td>apples</td>
<td>31.30%</td>
<td>2.74%</td>
</tr>
<tr>
<td>23</td>
<td>apples</td>
<td>83.96%</td>
<td>1.34%</td>
</tr>
<tr>
<td>24 (최종 출력)</td>
<td>apples</td>
<td>42.63%</td>
<td>24.57%</td>
</tr>
</tbody></table>
<p>앞쪽 20개 Block에서는 GPT-2처럼 1위가 뜻 없는 Token이다. 사전이 여러 언어로 되어 있어서 '日子', '겟', 'ракти' 같은 Token이 1위로 뜨기도 했다.</p>
<p>20번째 Block부터 1위가 gifts(선물), fruits(과일), apples(사과) 순서로 바뀐다. 1편에서 설명용으로 그린 '선물 → 민수가 좋아하는 것 → 사과' 흐름과 거의 같은 모습이 실제 모델에서 나왔다. 이번 실험에서 가장 반가웠던 장면이다.</p>
<p>여기서도 마지막 Block을 지나며 apples가 83.96%에서 42.63%로 줄고 grapes는 1.34%에서 24.57%로 오른다. 1번에서 본 GPT-2와 같은 방향이다.</p>
<h2 id="6-작은-모델을-직접-학습시키면">6. 작은 모델을 직접 학습시키면</h2>
<blockquote>
<p>학습을 아무리 해도 입력에 구분할 정보가 없으면 구분하지 못한다.</p>
</blockquote>
<p>GPT-2와 Qwen2.5는 이미 학습이 끝난 모델을 가져다 쓰기만 했다. 학습이 확률을 실제로 어떻게 바꾸는지는 직접 해 봐야 알 수 있다. 그래서 문장 4개로 아주 작은 모델 두 개를 학습했다.</p>
<pre><code>민수 는 사과 를 좋아해 .     지수 는 포도 를 좋아해 .
민수 는 사과 를 샀다 .       지수 는 포도 를 샀다 .</code></pre><p>Transformer가 아니라 한 층짜리 모델이다. 다만 다음 Token을 맞히고 틀린 만큼 가중치를 고치는 학습 방식은 LLM과 같다.</p>
<table>
<thead>
<tr>
<th>모델</th>
<th>입력으로 받는 정보</th>
</tr>
</thead>
<tbody><tr>
<td>A</td>
<td>바로 앞 Token 하나</td>
</tr>
<tr>
<td>B</td>
<td>바로 앞 Token + 앞에 나온 Token 전체의 비율</td>
</tr>
</tbody></table>
<p><sub>Loss: 모델이 틀린 정도. 정답 Token에 준 확률이 낮을수록 커진다</sub></p>
<p>'민수 는 ___' 다음 확률을 학습 중간중간 기록했다.</p>
<table>
<thead>
<tr>
<th>가중치 수정 횟수</th>
<th>0</th>
<th>10</th>
<th>50</th>
<th>200</th>
<th>500</th>
</tr>
</thead>
<tbody><tr>
<td>모델 A Loss</td>
<td>2.20</td>
<td>1.48</td>
<td>0.55</td>
<td>0.33</td>
<td>0.30</td>
</tr>
<tr>
<td>모델 A: 사과 / 포도</td>
<td>11% / 11%</td>
<td>21% / 21%</td>
<td>40% / 40%</td>
<td>48% / 48%</td>
<td>49% / 49%</td>
</tr>
<tr>
<td>모델 B Loss</td>
<td>2.20</td>
<td>1.31</td>
<td>0.42</td>
<td>0.20</td>
<td>0.16</td>
</tr>
<tr>
<td>모델 B: 사과 / 포도</td>
<td>11% / 11%</td>
<td>24% / 19%</td>
<td>60% / 24%</td>
<td>86% / 10%</td>
<td>94% / 5%</td>
</tr>
</tbody></table>
<p>처음에는 가중치가 모두 0이다. 그래서 사전에 있는 9개 Token이 똑같이 11%씩 받는다.</p>
<p>학습할수록 모델 B는 사과 쪽으로 기운다. 모델 A는 사과와 포도가 같이 오르다가 49%에서 멈춘다. 500번을 고쳐도 더 나아지지 않는다.</p>
<table>
<thead>
<tr>
<th>입력</th>
<th>모델 A</th>
<th>모델 B</th>
</tr>
</thead>
<tbody><tr>
<td>민수 는 ___</td>
<td>사과 49%, 포도 49%</td>
<td>사과 94%, 포도 5%</td>
</tr>
<tr>
<td>지수 는 ___</td>
<td>사과 49%, 포도 49%</td>
<td>포도 94%, 사과 5%</td>
</tr>
<tr>
<td>민수 는 사과 를 ___</td>
<td>좋아해 49%, 샀다 49%</td>
<td>좋아해 49%, 샀다 49%</td>
</tr>
</tbody></table>
<p>모델 A는 바로 앞의 '는'만 받는다. 그 앞에 민수가 있었는지 지수가 있었는지 모르니 반반으로 찍을 수밖에 없다. 모델 B는 앞에 '민수'가 있었다는 정보를 받아서 사과를 고른다.</p>
<p>Transformer에서 앞쪽 정보를 가져오는 일은 Self-Attention이 한다. 1편 4단계에서 Attention을 자동완성과 갈라지는 지점이라고 한 이유가 이 표에 있다.</p>
<p>마지막 줄도 볼 만하다. '좋아해'와 '샀다'는 학습 문장에서 실제로 반반이었다. 모델 B도 49% 대 49%를 낸다. 모델은 본 것 이상은 알지 못한다.</p>
<h2 id="정리">정리</h2>
<table>
<thead>
<tr>
<th>질문</th>
<th>확인한 것</th>
</tr>
</thead>
<tbody><tr>
<td>답은 언제 생기나</td>
<td>GPT-2는 12개 Block 중 10번째, Qwen2.5는 24개 중 22번째에서 apples가 1위가 된다</td>
</tr>
<tr>
<td>Attention은 어디를 보나</td>
<td>평균 56.2%가 첫 Token으로 간다(Attention Sink). 이를 빼면 Head마다 보는 곳이 다르다</td>
</tr>
<tr>
<td>논문과 지금 모델은 뭐가 다른가</td>
<td>Decoder만 남았고, 위치 정보와 정규화 위치 같은 부품이 바뀌었다. 뼈대는 같다</td>
</tr>
<tr>
<td>최근 모델은 더 잘하나</td>
<td>문맥(과일)은 Qwen2.5가 더 잘 잡았다. apples와 grapes를 가르는 건 GPT-2가 더 분명했다</td>
</tr>
<tr>
<td>학습은 무엇을 바꾸나</td>
<td>확률을 정답 쪽으로 옮긴다. 다만 입력에 없는 정보는 학습으로 만들 수 없다</td>
</tr>
</tbody></table>
<p>1편에서 그림으로만 그렸던 'Block을 여러 번 지나며 답이 좁혀진다'는 설명을 이번에는 실제 숫자로 확인했다. 특히 Qwen2.5에서 gifts → fruits → apples 순서가 그대로 찍힌 것은 직접 돌려 보기 전까지는 기대하지 않았던 결과였다.</p>
<h2 id="직접-해-보려면">직접 해 보려면</h2>
<table>
<thead>
<tr>
<th>도구</th>
<th>해 볼 것</th>
</tr>
</thead>
<tbody><tr>
<td>Transformer Explainer</td>
<td>브라우저에서 GPT-2에 문장을 넣고 Attention 비율과 Temperature 효과를 본다</td>
</tr>
<tr>
<td>Tiktokenizer</td>
<td>같은 문장이 모델마다 몇 Token으로 잘리는지 본다</td>
</tr>
<tr>
<td>build-nanogpt</td>
<td>GPT-2를 코드로 처음부터 만들어 학습한다. GPU가 있으면 좋다</td>
</tr>
</tbody></table>
<h2 id="references">References</h2>
<ul>
<li>Vaswani et al., Attention Is All You Need, 2017. <a href="https://arxiv.org/abs/1706.03762">https://arxiv.org/abs/1706.03762</a></li>
<li>Radford et al., Language Models are Unsupervised Multitask Learners (GPT-2), 2019</li>
<li>nostalgebraist, interpreting GPT: the logit lens, 2020</li>
<li>Xiao et al., Efficient Streaming Language Models with Attention Sinks, 2023. <a href="https://arxiv.org/abs/2309.17453">https://arxiv.org/abs/2309.17453</a></li>
<li>Su et al., RoFormer: Enhanced Transformer with Rotary Position Embedding, 2021. <a href="https://arxiv.org/abs/2104.09864">https://arxiv.org/abs/2104.09864</a></li>
<li>Meta, The Llama 3 Herd of Models, 2024. <a href="https://arxiv.org/abs/2407.21783">https://arxiv.org/abs/2407.21783</a></li>
<li>Qwen Team, Qwen2.5 Technical Report, 2024. <a href="https://arxiv.org/abs/2412.15115">https://arxiv.org/abs/2412.15115</a></li>
<li>Transformer Explainer. <a href="https://poloclub.github.io/transformer-explainer">https://poloclub.github.io/transformer-explainer</a></li>
<li>build-nanogpt. <a href="https://github.com/karpathy/build-nanogpt">https://github.com/karpathy/build-nanogpt</a></li>
</ul>