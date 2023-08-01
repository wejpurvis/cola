from plum import dispatch
from cola.ops import Array
from cola.ops import LinearOperator, Triangular
from cola.ops import Diagonal, Kronecker, BlockDiag, Product
from cola.utils import export
from cola.annotations import SelfAdjoint
from cola.algorithms import stochastic_lanczos_quad

@dispatch
@export
def logdet(A: LinearOperator, tol=1e-7, info=False, pbar=True) -> Array:
    # add casework
    raise NotImplementedError

@dispatch(cond=lambda A: A.isa(SelfAdjoint))
def logdet(A: LinearOperator, **kwargs) -> Array:
    xnp = A.ops
    trace_log_A = stochastic_lanczos_quad(A, xnp.log, **kwargs)
    return trace_log_A

@dispatch(cond = lambda A, **kwargs: all([(Ai.shape[-2] == Ai.shape[-1]) for Ai in A.Ms]))
def logdet(A: Product, **kwargs) -> Array:
    return sum(logdet(Ai) for Ai in A.Ms)

@dispatch
def logdet(A: Diagonal, **kwargs) -> Array:
    xnp = A.ops
    out = xnp.sum(xnp.log(A.diag))
    return out


@dispatch
def logdet(A: Kronecker, **kwargs) -> Array:
    # logdet(Pi A_i \otimes I) = sum_i logdet(A_i)
    return sum(logdet(A.Ai) for Ai in A.Ms)


@dispatch
def logdet(A: BlockDiag, **kwargs) -> Array:
    # logdet(\bigoplus A_i) = log \prod det(A_i) = sum_i logdet(A_i)
    return sum(logdet(A.Ai) for Ai in A.Ms)

@dispatch
def logdet(A: Triangular, **kwargs) -> Array:
    xnp = A.ops
    return xnp.sum(xnp.log(xnp.diag(A.A)))