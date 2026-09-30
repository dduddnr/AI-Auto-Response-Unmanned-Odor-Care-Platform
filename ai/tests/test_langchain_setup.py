"""LangChain 설치 확인용 스모크 테스트. 네트워크·DB·LLM 없이 돈다."""

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter


def test_runnable_chain():
    chain = RunnableLambda(lambda s: s.strip()) | RunnableLambda(lambda s: f"[{s}]")
    assert chain.invoke("  황화수소  ") == "[황화수소]"


def test_text_splitter_korean():
    text = "제1조(목적) 이 법은 악취를 방지함을 목적으로 한다.\n\n제2조(정의) 이 법에서 사용하는 용어의 뜻은 다음과 같다."
    chunks = RecursiveCharacterTextSplitter(chunk_size=40, chunk_overlap=0).split_text(text)
    assert chunks[0].startswith("제1조")
    assert any(c.startswith("제2조") for c in chunks)


def test_fake_embedding_dimension():
    # 3차 회의 스키마의 chunks.embedding VECTOR(1024)에 맞춘 차원
    vec = DeterministicFakeEmbedding(size=1024).embed_query("악취")
    assert len(vec) == 1024


def test_integration_packages_import():
    import langchain  # noqa: F401
    from langchain_ollama import OllamaEmbeddings  # noqa: F401
    from langchain_postgres import PGVector  # noqa: F401
