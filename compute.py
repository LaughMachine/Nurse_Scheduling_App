import numpy as np
from scipy.optimize import brentq

def heuristic_empty(x_bar, u_fixed, tau, s, mu, lbda_bar, b1, g, ded, N):
    new_alloc = []
    remaining_alloc = 1
    u_bar = [u/float(N) for u in u_fixed]
    for ind, x in enumerate(x_bar):
        a = u_bar[ind]
        b = 1
        traj_dummy, below_bool = get_vary_trajectory_u_bool(b, tau, s, x_bar[ind], mu[ind], lbda_bar[ind], g[ind], b1[ind])
        if not below_bool:
            new_alloc.append(min(b, remaining_alloc))
            remaining_alloc -= min(b, remaining_alloc)
        else:
            traj_dummy, below_bool = get_vary_trajectory_u_bool(a, tau, s, x_bar[ind], mu[ind], lbda_bar[ind], g[ind],
                                                                b1[ind])
            if below_bool:
                new_alloc.append(min(a, remaining_alloc))
                remaining_alloc -= min(a, remaining_alloc)
            else:
                while b - a > 0.0001:
                    midpoint = (b + a)*.5
                    traj_dummy, below_bool = get_vary_trajectory_u_bool(midpoint, tau, s, x_bar[ind], mu[ind], lbda_bar[ind], g[ind], b1[ind])
                    if below_bool:
                        b = midpoint
                    else:
                        a = midpoint
                new_alloc.append(a)
    if sum(new_alloc) < 1:
        remaining_alloc = 1 - sum(new_alloc)
        for i in range(len(new_alloc)):
            new_alloc[i] += ded[i] * remaining_alloc
        print new_alloc
    else:
        total = sum(new_alloc)
        new_alloc = [x/float(total) for x in new_alloc]
    u_alloc = [x - u_bar[ind] for ind, x in enumerate(new_alloc)]
    total_u = sum(u_alloc)
    if total_u == 0:
        actual_alloc = round_standard(u_bar, N)
    else:
        new_u_alloc = [x/float(total_u) for x in u_alloc]
        alloc = round_standard(new_u_alloc, N - sum(u_fixed))
        actual_alloc = [x + u_fixed[ind] for ind, x in enumerate(alloc)]
    return actual_alloc, new_alloc

def two_part_heuristic_empty(x_bar, tau, s, mu, lbda_bar, b1, g, ded, N, N0):
    alloc, unrounded_alloc = heuristic_empty(x_bar, tau, s, mu, lbda_bar, b1, g, ded, N)
    end_traj = []
    rounded_alloc = [i/float(N0) for i in alloc]
    rounded_alloc_norm = [i/float(N) for i in alloc]
    for ind, i in enumerate(rounded_alloc):
        traj_dummy, below_bool = get_vary_trajectory_u_bool(i, tau, s, x_bar[ind], mu[ind], lbda_bar[ind], g[ind], b1[ind])
        end_traj.append(traj_dummy)
    alloc_2, unrounded_alloc_2 = heuristic_empty(end_traj[:3], tau, s, mu[:3], lbda_bar[:3], b1, g[:3], ded[:3], N)
    new_alloc = [rounded_alloc_norm[3]*i+rounded_alloc_norm[ind] for ind, i in enumerate(unrounded_alloc_2)]
    print new_alloc
    final_alloc = round_standard(new_alloc, N)
    final_alloc.append(0)
    return alloc, final_alloc

def three_class_heuristic_empty(x_bar, tau, s, mu, lbda_bar, b1, g, ded, N):
    alloc, unrounded_alloc = heuristic_empty(x_bar[:3], tau, s, mu[:3], lbda_bar[:3], b1, g[:3], ded[:3], N)
    alloc.append(0)
    return alloc

def get_vary_trajectory_u_bool(u, tau, s, z0, mu, l, g, b, target=0):
    t, hl = find_transition(tau, s, z0, mu, l, g, u, b)
    start_h = z0
    if start_h < u:
        below_bool = True
    else:
        below_bool = False
    if t == -1 or t > tau:
        if hl:
            traj = g_t(tau, s, z0, mu, l, g, u, b)
        else:
            traj = z_t(tau, s, z0, mu, l, g, u, b)
            below_bool = True
    else:
        start_h = u
        prev_t = t
        while t < tau:
            t_new, hl = find_transition(tau - t, s + t, u, mu, l, g, u, b)
            if not hl:
                below_bool = True
            if t_new == -1:
                prev_t = t
                break
            prev_t = t
            t += t_new
            start_h = u
        if hl:
            traj = g_t(tau - prev_t, s + prev_t, start_h, mu, l, g, u, b)
        else:
            traj = z_t(tau - prev_t, s + prev_t, start_h, mu, l, g, u, b)
            below_bool = True
    return traj+u-target, below_bool

# Below capacity trajectory
def z_t(t, s, z0, mu, l, g, u, b):
    first_block = (z0*mu+l*(np.exp(mu*t)-1))*(g**2*mu**2+np.pi**2)
    second_block = np.exp(mu*t)*(g*mu*np.sin(np.pi*(t+s)/g)-np.pi*np.cos(np.pi*(t+s)/g))
    third_block = -g*mu*np.sin(np.pi*s/g) + np.pi*np.cos(np.pi*s/g)
    mult_block = np.exp(-mu*t)/(mu*(g**2*mu**2+np.pi**2))

    return (first_block + (second_block + third_block)*g*b*mu)*mult_block - u

# Above capacity trajectory
def g_t(t, s, z0, mu, l, g, u, b):
    return z0 + l*t - mu*t*u + g*b*np.cos(np.pi*s/g)/(np.pi) - g*b*np.cos(np.pi*(t+s)/g)/(np.pi) - u

def find_transition(t, s, z0, mu, l, g, u, b):
    # Check if initial state is above or below capacity
    if z0 < u:
        use_g = False
    elif z0 > u:
        use_g = True
    # If we are at capacity, we check if the arrival rate is increasing or decreasing
    else:
        if z_t(0.000001, s, z0, mu, l, g, u, b) > 0 and g_t(0.000001, s, z0, mu, l, g, u, b) > 0:
            use_g = True
        elif z_t(0.000001, s, z0, mu, l, g, u, b) < 0 and g_t(0.000001, s, z0, mu, l, g, u, b) < 0:
            use_g = False
        else:
            if round(lbda_t(s, l, b), 5) > round(u * mu, 5):
                use_g = True
            elif round(lbda_t(s, l, b), 5) < round(u * mu, 5):
                use_g = False
            # If the arrival rate equal to u*mu then we check if it is increasing or decreasing
            else:
                if np.cos(s * np.pi / g) < 0:
                    use_g = False
                elif np.cos(s * np.pi / g) > 0:
                    use_g = True
                else:
                    if np.sin(s * np.pi / g) > 0:
                        use_g = False
                    else:
                        use_g = True
    # If use_g is true, the trajectory will be above capacity, otherwise it will go below capacity
    if use_g:
        # Check if service rate is greater than arrival rates at all times or less at all times
        test_val = (u * mu - l)*2/l
        # Service rate will be less than all arrival rates (trajectory will grow existing queue)
        if test_val <= -1.0:
            return -1, use_g
        # Service rate will be greater than all arrival rates (trajectory will always decrease queue)
        elif test_val >= 1.0:
            low = t
        # When service rate is within the range of arrival rates, trajectory can cross capacity more than once
        else:
            low = (2 * g - s + np.arcsin(test_val) * g / np.pi) % (2 * g)
            counter = 1
            # We check local minima until it is out of the shift period
            while low < t and g_t(low, s, z0, mu, l, g, u, b) > 0:
                low = (2 * g - s + np.arcsin(test_val) * g / np.pi) % (2 * g) + 2*g*counter
                counter += 1
        # We calculate the headcount at found local minima and check if it is below capacity
        val = g_t(low, s, z0, mu, l, g, u, b)
        # If the headcount at the local minima is below capacity we have potentially found a transition point
        if val > 0:
            return -1, use_g
        else:
            # Need to find starting point where queue is above capacity, since val < 0 we will find a transition point
            if z0 > u:
                new_result = brentq(g_t, 0, low, args=(s, z0, mu, l, g, u, b))
            else:
                if g_t(0.000001, s, z0, mu, l, g, u, b) < 0:
                    print 'precision error'
                    use_g = False
                    high = (3 * g - s - np.arcsin((u * mu - l) * 2 / l) * g / np.pi) % (2 * g)
                    counter = 1
                    # We check local minima until it is out of the shift period or if sufficient value is found
                    while high < t and z_t(high, s, z0, mu, l, g, u, b) < 0:
                        high = (3 * g - s - np.arcsin((u * mu - l) * 2 / l) * g / np.pi) % (2 * g) + 2 * g * counter
                        counter += 1
                    val = z_t(high, s, z0, mu, l, g, u, b)
                    if val < 0:
                        return -1, use_g
                    else:
                        new_result = brentq(z_t, 0.000001, high, args=(s, z0, mu, l, g, u, b))
                else:
                    new_result = brentq(g_t, 0.000001, low, args=(s, z0, mu, l, g, u, b))
    # If use_g is False then the trajectory will be below capacity, thus we use z_t
    else:
        # Check if service rate is greater than arrival rates at all times or less at all times
        test_val = (u * mu - l) * 2 / l
        # Service rate will be less than all arrival rates (trajectory will grow existing queue)
        if test_val <= -1.0:
            high = t
        # Service rate will be greater than all arrival rates (trajectory will always be below capacity)
        elif test_val >= 1.0:
            return -1, use_g
        # When service rate is within the range of arrival rates, trajectory can cross capacity more than once
        else:
            high = (3 * g - s - np.arcsin((u * mu - l) * 2 / l) * g / np.pi) % (2 * g)
            counter = 1
            # We check local minima until it is out of the shift period or if sufficient value is found
            while high < t and z_t(high, s, z0, mu, l, g, u, b) < 0:
                high = (3 * g - s - np.arcsin((u * mu - l) * 2 / l) * g / np.pi) % (2 * g) + 2 * g * counter
                counter += 1
        val = z_t(high, s, z0, mu, l, g, u, b)
        if val < 0:
            return -1, use_g
        else:
            if z0 < u:
                new_result = brentq(z_t, 0, high, args=(s, z0, mu, l, g, u, b))
            else:
                if z_t(0.000001, s, z0, mu, l, g, u, b) > 0:
                    print 'precision error'
                    use_g = True
                    low = (2 * g - s + np.arcsin(test_val) * g / np.pi) % (2 * g)
                    counter = 1
                    # We check local minima until it is out of the shift period
                    while low < t and g_t(low, s, z0, mu, l, g, u, b) > 0:
                        low = (2 * g - s + np.arcsin(test_val) * g / np.pi) % (2 * g) + 2 * g * counter
                        counter += 1
                    val = g_t(low, s, z0, mu, l, g, u, b)
                    if val < 0:
                        return -1, use_g
                    else:
                        new_result = brentq(g_t, 0.000001, low, args=(s, z0, mu, l, g, u, b))
                else:
                    new_result = brentq(z_t, 0.000001, high, args=(s, z0, mu, l, g, u, b))
    return new_result, use_g

def round_standard(solution, N):
    alloc = []
    diff = []
    classes = len(solution)-1
    for ind, u in enumerate(solution):
        n = np.floor(u * N)
        alloc.append(n)
        diff.append((abs(u - n / float(N)), classes-ind))
    s_diff = sorted(diff, reverse=True)
    s_ind = 0
    while sum(alloc) < N:
        alloc[classes - s_diff[s_ind][1]] += 1
        s_ind += 1
    return alloc

def lbda_t(t, a, b):
    return a + b*np.sin(np.pi*(t)/12.0)/2.0
