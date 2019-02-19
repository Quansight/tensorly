"""
Core operations on Kruskal tensors.
"""

import tensorly as tl
from . import backend as T

# Author: Jean Kossaifi

# License: BSD 3 clause


def kruskal_to_tensor(factors, weights=None, mask=None):
    """
    Turns the Khatri-product of matrices into a full tensor

        ``factor_matrices = [|U_1, ... U_n|]`` becomes
        a tensor shape ``(U[1].shape[0], U[2].shape[0], ... U[-1].shape[0])``

    Parameters
    ----------
    factors : ndarray list
        list of factor matrices, all with the same number of columns
        i.e. for all matrix U in factor_matrices:
        U has shape ``(s_i, R)``, where R is fixed and s_i varies with i

    mask : ndarray a mask to be applied to the final tensor. It should be
        broadcastable to the shape of the final tensor, that is
        ``(U[1].shape[0], ... U[-1].shape[0])``.

    Returns
    -------
    ndarray
        full tensor of shape ``(U[1].shape[0], ... U[-1].shape[0])``

    Notes
    -----
    This version works by first computing the mode-0 unfolding of the tensor
    and then refolding it.

    There are other possible and equivalent alternate implementation, e.g.
    summing over r and updating an outer product of vectors.

    """
    from .tenalg import khatri_rao
    shape = [T.shape(factor)[0] for factor in factors]
    if weights is not None:
        factors[0] = factors[0]*weights
        full_tensor = T.sum(khatri_rao(factors, mask=mask), axis=1)
    else:
        full_tensor = T.sum(khatri_rao(factors, mask=mask), axis=1)
    return tl.fold(full_tensor, 0, shape)


def kruskal_to_unfolded(factors, mode):
    """Turns the khatri-product of matrices into an unfolded tensor

        turns ``factors = [|U_1, ... U_n|]`` into a mode-`mode`
        unfolding of the tensor

    Parameters
    ----------
    factors : ndarray list
        list of matrices, all with the same number of columns
        ie for all u in factor_matrices:
        u[i] has shape (s_u_i, R), where R is fixed
    mode: int
        mode of the desired unfolding

    Returns
    -------
    ndarray
        unfolded tensor of shape (tensor_shape[mode], -1)

    Notes
    -----
    Writing factors = [U_1, ..., U_n], we exploit the fact that
    ``U_k = U[k].dot(khatri_rao(U_1, ..., U_k-1, U_k+1, ..., U_n))``
    """
    from .tenalg import khatri_rao
    return T.dot(factors[mode], T.transpose(khatri_rao(factors, skip_matrix=mode)))


def kruskal_to_vec(factors):
    """Turns the khatri-product of matrices into a vector

        (the tensor ``factors = [|U_1, ... U_n|]``
        is converted into a raveled mode-0 unfolding)

    Parameters
    ----------
    factors : ndarray list
        list of matrices, all with the same number of columns
        i.e.::

            for u in U:
                u[i].shape == (s_i, R)

        where `R` is fixed while `s_i` can vary with `i`

    Returns
    -------
    ndarray
        vectorised tensor
    """
    return tl.tensor_to_vec(kruskal_to_tensor(factors))
