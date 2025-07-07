from langchain.schema import HumanMessage
from ..lib import AgentState, Context

def bootstrap_codebase(state: AgentState, context: Context) -> AgentState:
    """
    1) Enumerate every file in the project.
    2) Run ctags-based symbol indexing only over that manifest.
    3) Store both in AgentState for downstream nodes.
    """
    # 1) Enumerate files
    file_paths = context.tools["file_enumerate"]._run()
    state.file_manifest = file_paths
    state.messages.append(
        HumanMessage(content=f"Bootstrapped: found {len(file_paths)} files.")
    )

    # 2) Index symbols in exactly those files
    symbol_index = context.tools["symbol_index"]._run(file_paths=file_paths)
    state.symbol_index = symbol_index
    state.messages.append(
        HumanMessage(content=f"Indexed symbols in {len(symbol_index)} files.")
    )

    return state
