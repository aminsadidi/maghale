"""Analytic angular distribution of a point dipole above a glass half-space (angular-spectrum / Fresnel method).
Medium 1 (z > 0, n1) contains the dipole at height h; medium 2 (z < 0, n2) is the substrate. The far field in each
direction is obtained from the plane-wave spectrum: upward = direct + reflected waves, downward = transmitted waves
(including the 'forbidden' light from evanescent components, which become propagating in the glass).
Returns the power per solid angle; integrated power relative to the free dipole gives the radiative rate.
usage: python isi/analysis/glass_check.py"""
import numpy as np

def fresnel(kx, k1, k2, eps1, eps2):
    kz1 = np.sqrt(k1**2 - kx**2 + 0j); kz2 = np.sqrt(k2**2 - kx**2 + 0j)
    rs = (kz1 - kz2) / (kz1 + kz2); ts = 2 * kz1 / (kz1 + kz2)
    rp = (eps2 * kz1 - eps1 * kz2) / (eps2 * kz1 + eps1 * kz2); tp = 2 * eps2 * kz1 / (eps2 * kz1 + eps1 * kz2) * np.sqrt(eps1 / eps2)
    return kz1, kz2, rs, rp, ts, tp

def pattern(p, h, lam, n1=1.0, n2=1.52, nth=721, nph=181):
    """dP/dOmega on upper (theta in medium 1 from +z) and lower (theta2 from -z, medium 2) hemispheres, for dipole p."""
    k0 = 2 * np.pi / lam; k1, k2 = n1 * k0, n2 * k0; e1, e2 = n1**2, n2**2
    th = (np.arange(nth) + 0.5) * (np.pi / 2) / nth; ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    T, P = np.meshgrid(th, ph, indexing='ij')
    out = {}
    for side in ('up', 'down'):
        kk = k1 if side == 'up' else k2
        kx = kk * np.sin(T); kz1, kz2, rs, rp, ts, tp = fresnel(kx, k1, k2, e1, e2)
        # unit vectors of s and p polarisation for a plane wave with in-plane direction (cos ph, sin ph)
        es = np.stack([-np.sin(P), np.cos(P), 0 * P])
        def ep(kxv, kz, k, sgn):   # p-unit vector for wavevector (kx cos, kx sin, sgn*kz), |k| = k
            return np.stack([-sgn * kz * np.cos(P), -sgn * kz * np.sin(P), kxv]) / k
        pv = np.array(p, float)[:, None, None]
        # amplitudes of the dipole field projected on s and p for upward (+) and downward (-) waves in medium 1
        a_s = np.sum(es * pv, 0)
        a_p_up = np.sum(ep(kx, kz1, k1, +1) * pv, 0); a_p_dn = np.sum(ep(kx, kz1, k1, -1) * pv, 0)
        # far field E_inf ~ k_j cos(theta_j) * (angular spectrum ~ 1/kz1): for the upper side k1 cos(theta) = kz1 and the
        # factors cancel; for the lower side t_s, t_p contain kz1 so that t/kz1 stays finite at the critical angle.
        if side == 'up':
            ph_d = np.exp(-1j * kz1 * h); ph_r = np.exp(1j * kz1 * h)      # relative to the plane z = 0, observer above
            Es = a_s * (ph_d + rs * ph_r)
            Ep = a_p_up * ph_d + rp * a_p_dn * ph_r
            far = (np.abs(Es)**2 + np.abs(Ep)**2) * n1
        else:
            ph_t = np.exp(1j * kz1 * h)
            ts_k = 2 / (kz1 + kz2); tp_k = 2 * e2 / (e2 * kz1 + e1 * kz2) * np.sqrt(e1 / e2)
            Es = a_s * ts_k * ph_t
            Ep = a_p_dn * tp_k * ph_t
            far = (k2 * np.cos(T))**2 * (np.abs(Es)**2 + np.abs(Ep)**2) * n2
        out[side] = (th, ph, np.real(far))
    return out

def fractions(p, h, lam, NAs_air=(0.9,), NAs_glass=(1.3, 1.45), n2=1.52):
    o = pattern(p, h, lam, n2=n2)
    def integ(th, ph, f, thmax=np.pi / 2):
        dth = th[1] - th[0]; m = th <= thmax
        return np.sum(np.mean(f[m], 1) * 2 * np.pi * np.sin(th[m])) * dth
    up, dn = integ(*o['up']), integ(*o['down']); tot = up + dn
    r = {'up': up / tot, 'down': dn / tot}
    for na in NAs_air: r[f'air_NA{na}'] = integ(*o['up'], np.arcsin(na)) / tot
    for na in NAs_glass:
        if na < n2: r[f'glass_NA{na}'] = integ(*o['down'], np.arcsin(na / n2)) / tot
    r['tot_rel'] = tot
    return r

if __name__ == '__main__':
    # sanity: n2 = 1 must give 1/2 up, 1/2 down
    for p in ([1, 0, 0], [0, 0, 1]):
        r = fractions(p, 11, 630, n2=1.0); print('n2=1', p, {k: round(float(v), 4) for k, v in r.items()})
    free = {tuple(p): fractions(p, 11, 630, n2=1.0)['tot_rel'] for p in ([1, 0, 0], [0, 0, 1])}
    for p in ([1, 0, 0], [0, 1, 0], [0, 0, 1]):
        r = fractions(p, 10.97, 630); key = (1, 0, 0) if p[2] == 0 else (0, 0, 1)
        print('glass', p, {k: round(float(v), 4) for k, v in r.items() if k != 'tot_rel'}, 'rad rate / free =', round(float(r['tot_rel'] / free[key]), 3))


def reciprocity_pattern(p, h, lam, n1=1.0, n2=1.52, nth=181, nph=72):
    """Same quantity from reciprocity: dP/dOmega(s, e) ~ n_j |p . E_loc|^2, E_loc = field at the dipole of a
    unit-amplitude plane wave incident from direction s in medium j (propagating along -s), polarisation e."""
    k0 = 2 * np.pi / lam; k1, k2 = n1 * k0, n2 * k0; e1, e2 = n1**2, n2**2
    th = (np.arange(nth) + 0.5) * (np.pi / 2) / nth; ph = (np.arange(nph) + 0.5) * 2 * np.pi / nph
    T, P = np.meshgrid(th, ph, indexing='ij'); pv = np.array(p, float)
    res = {}
    for side in ('up', 'down'):
        kk = k1 if side == 'up' else k2
        kx = kk * np.sin(T); kz1, kz2, rs, rp, ts, tp = fresnel(kx, k1, k2, e1, e2)
        cP, sP = np.cos(P), np.sin(P)
        es = np.stack([-sP, cP, 0 * P])
        if side == 'up':      # incident wave travels downward in medium 1: k = (-kx c, -kx s, -kz1)
            # s: incident + reflected (r_s); p: incident p-vector + reflected p-vector (r_p)
            epi = np.stack([kz1 * cP, kz1 * sP, kx]) / k1          # p-unit vector, downward wave (sign convention)
            epr = np.stack([-kz1 * cP, -kz1 * sP, kx]) / k1        # p-unit vector of reflected (upward) wave
            ph_i = np.exp(-1j * kz1 * h); ph_r = np.exp(1j * kz1 * h) # phases at the dipole height (z = h)
            Es = es * (ph_i + rs * ph_r)
            Ep = epi * ph_i + epr * rp * ph_r
        else:                 # incident from glass travelling upward; transmitted into medium 1 (k1 frame)
            rs2 = (kz2 - kz1) / (kz2 + kz1); ts2 = 2 * kz2 / (kz1 + kz2)
            tp2 = 2 * e1 * kz2 / (e1 * kz2 + e2 * kz1) * np.sqrt(e2 / e1)
            ept = np.stack([-kz1 * cP, -kz1 * sP, kx]) / k1        # p-unit vector of transmitted upward wave in medium 1
            pht = np.exp(1j * kz1 * h)
            Es = es * ts2 * pht
            Ep = ept * tp2 * pht
        nj = n1 if side == 'up' else n2
        f = nj * (np.abs(np.tensordot(pv, Es, 1))**2 + np.abs(np.tensordot(pv, Ep, 1))**2)
        res[side] = (th, ph, np.real(f))
    return res


def recip_fractions(p, h, lam, n2=1.52):
    o = reciprocity_pattern(p, h, lam, n2=n2)
    def integ(th, ph, f, thmax=np.pi / 2):
        dth = th[1] - th[0]; m = th <= thmax
        return np.sum(np.mean(f[m], 1) * 2 * np.pi * np.sin(th[m])) * dth
    up, dn = integ(*o['up']), integ(*o['down']); tot = up + dn
    return {'down': dn / tot, 'glass_NA1.3': integ(*o['down'], np.arcsin(1.3 / n2)) / tot,
            'glass_NA1.45': integ(*o['down'], np.arcsin(1.45 / n2)) / tot, 'air_NA0.9': integ(*o['up'], np.arcsin(0.9)) / tot,
            'tot_rel': tot}
