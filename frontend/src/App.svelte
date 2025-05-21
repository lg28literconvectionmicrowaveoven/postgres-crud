<script>
  import { onMount } from 'svelte';

  // App states
  let isLoggedIn = false;
  let isLoading = false;
  let error = '';
  let successMessage = '';
  let token = '';
  let username = '';
  let email = '';
  let currentView = 'login'; // 'login', 'signup', 'dashboard', 'change-password'
  
  // Form data
  let loginEmail = '';
  let loginPassword = '';
  let signupUsername = '';
  let signupEmail = '';
  let signupPassword = '';
  let signupConfirmPassword = '';
  let newPassword = '';
  let newPasswordConfirm = '';

  // API base URL - adjust as needed for your environment
  const API_URL = 'http://127.0.0.1:8000';

  onMount(() => {
    // Check for saved token in localStorage
    const savedToken = localStorage.getItem('authToken');
    const savedUsername = localStorage.getItem('username');
    
    if (savedToken) {
      token = savedToken;
      username = savedUsername || '';
      validateToken(savedToken);
    }
  });

  async function validateToken(authToken) {
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(`${API_URL}/?token=${authToken}`);
      
      if (response.ok) {
        const data = await response.json();
        isLoggedIn = true;
        email = data.email;
        username = data.user_name;
        currentView = 'dashboard';
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('username', username);
      } else {
        // Token is invalid, clear localStorage
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        isLoggedIn = false;
        currentView = 'login';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
      isLoggedIn = false;
    } finally {
      isLoading = false;
    }
  }

  async function handleLogin() {
    if (!loginEmail || !loginPassword) {
      error = 'Please fill in all fields';
      return;
    }
    
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(`${API_URL}/login?email=${encodeURIComponent(loginEmail)}&password=${encodeURIComponent(loginPassword)}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        token = data.token;
        username = data.user_name;
        email = loginEmail;
        isLoggedIn = true;
        currentView = 'dashboard';
        
        // Save to localStorage
        localStorage.setItem('authToken', token);
        localStorage.setItem('username', username);
        
        // Clear form
        loginEmail = '';
        loginPassword = '';
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'Login failed';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function handleSignup() {
    if (!signupUsername || !signupEmail || !signupPassword || !signupConfirmPassword) {
      error = 'Please fill in all fields';
      return;
    }
    
    if (signupPassword !== signupConfirmPassword) {
      error = 'Passwords do not match';
      return;
    }
    
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(
        `${API_URL}/signup?username=${encodeURIComponent(signupUsername)}&email=${encodeURIComponent(signupEmail)}&password=${encodeURIComponent(signupPassword)}`, 
        {
          method: 'POST'
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        token = data.token;
        isLoggedIn = true;
        email = signupEmail;
        username = signupUsername;
        currentView = 'dashboard';
        
        // Save to localStorage
        localStorage.setItem('authToken', token);
        localStorage.setItem('username', username);
        
        // Clear form
        signupUsername = '';
        signupEmail = '';
        signupPassword = '';
        signupConfirmPassword = '';
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'Signup failed';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function handleChangePassword() {
    if (!newPassword || !newPasswordConfirm) {
      error = 'Please fill in all fields';
      return;
    }
    
    if (newPassword !== newPasswordConfirm) {
      error = 'Passwords do not match';
      return;
    }
    
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(
        `${API_URL}/change-password?token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(newPassword)}`,
        {
          method: 'POST'
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        token = data.token;
        
        // Update localStorage
        localStorage.setItem('authToken', token);
        
        // Clear form and show success message
        newPassword = '';
        newPasswordConfirm = '';
        successMessage = 'Password changed successfully';
        setTimeout(() => successMessage = '', 3000);
        currentView = 'dashboard';
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'Failed to change password';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function handleLogout() {
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(`${API_URL}/logout?token=${encodeURIComponent(token)}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        // Clear states and localStorage
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        token = '';
        username = '';
        email = '';
        isLoggedIn = false;
        currentView = 'login';
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'Logout failed';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function handleDeleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }
    
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(`${API_URL}/delete-account?token=${encodeURIComponent(token)}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Clear states and localStorage
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        token = '';
        username = '';
        email = '';
        isLoggedIn = false;
        currentView = 'login';
        successMessage = 'Account deleted successfully';
        setTimeout(() => successMessage = '', 3000);
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'Failed to delete account';
      }
    } catch (err) {
      error = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function switchView(view) {
    error = '';
    currentView = view;
  }
</script>

<main class="container">
  <div class="auth-container">
    <h1 class="app-title">Auth App</h1>
    
    {#if error}
      <div class="alert alert-error">
        {error}
      </div>
    {/if}
    
    {#if successMessage}
      <div class="alert alert-success">
        {successMessage}
      </div>
    {/if}
    
    {#if isLoading}
      <div class="loading">Loading...</div>
    {:else}
      <!-- Login Form -->
      {#if currentView === 'login'}
        <div class="auth-form">
          <h2>Login</h2>
          <form on:submit|preventDefault={handleLogin}>
            <div class="form-group">
              <label for="login-email">Email</label>
              <input 
                type="email" 
                id="login-email" 
                bind:value={loginEmail} 
                placeholder="Email"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="login-password">Password</label>
              <input 
                type="password" 
                id="login-password" 
                bind:value={loginPassword} 
                placeholder="Password"
                required
              />
            </div>
            
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
          
          <p class="form-switch">
            Don't have an account? 
            <button class="link-button" on:click={() => switchView('signup')}>Sign up</button>
          </p>
        </div>
      
      <!-- Signup Form -->
      {:else if currentView === 'signup'}
        <div class="auth-form">
          <h2>Create Account</h2>
          <form on:submit|preventDefault={handleSignup}>
            <div class="form-group">
              <label for="signup-username">Username</label>
              <input 
                type="text" 
                id="signup-username" 
                bind:value={signupUsername} 
                placeholder="Username"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="signup-email">Email</label>
              <input 
                type="email" 
                id="signup-email" 
                bind:value={signupEmail} 
                placeholder="Email"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="signup-password">Password</label>
              <input 
                type="password" 
                id="signup-password" 
                bind:value={signupPassword} 
                placeholder="Password"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="signup-confirm">Confirm Password</label>
              <input 
                type="password" 
                id="signup-confirm" 
                bind:value={signupConfirmPassword} 
                placeholder="Confirm Password"
                required
              />
            </div>
            
            <button type="submit" class="btn btn-primary">Sign Up</button>
          </form>
          
          <p class="form-switch">
            Already have an account? 
            <button class="link-button" on:click={() => switchView('login')}>Login</button>
          </p>
        </div>
      
      <!-- Dashboard -->
      {:else if currentView === 'dashboard'}
        <div class="dashboard">
          <h2>Welcome, {username}!</h2>
          
          <div class="user-info">
            <p><strong>Email:</strong> {email}</p>
          </div>
          
          <div class="dashboard-actions">
            <button class="btn btn-secondary" on:click={() => switchView('change-password')}>
              Change Password
            </button>
            <button class="btn btn-primary" on:click={handleLogout}>
              Logout
            </button>
            <button class="btn btn-danger" on:click={handleDeleteAccount}>
              Delete Account
            </button>
          </div>
        </div>
      
      <!-- Change Password Form -->
      {:else if currentView === 'change-password'}
        <div class="auth-form">
          <h2>Change Password</h2>
          <form on:submit|preventDefault={handleChangePassword}>
            <div class="form-group">
              <label for="new-password">New Password</label>
              <input 
                type="password" 
                id="new-password" 
                bind:value={newPassword} 
                placeholder="New Password"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="confirm-new-password">Confirm New Password</label>
              <input 
                type="password" 
                id="confirm-new-password" 
                bind:value={newPasswordConfirm} 
                placeholder="Confirm New Password"
                required
              />
            </div>
            
            <div class="form-buttons">
              <button type="button" class="btn btn-secondary" on:click={() => switchView('dashboard')}>
                Cancel
              </button>
              <button type="submit" class="btn btn-primary">
                Change Password
              </button>
            </div>
          </form>
        </div>
      {/if}
    {/if}
  </div>
</main>

<style>
  :global(body) {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f7fa;
  }
  
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 2rem;
  }
  
  .auth-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    width: 100%;
    max-width: 450px;
  }
  
  .app-title {
    text-align: center;
    color: #3a4374;
    margin-bottom: 1.5rem;
  }
  
  .auth-form h2, .dashboard h2 {
    color: #3a4374;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .form-group {
    margin-bottom: 1.2rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #535a77;
  }
  
  input {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
  }
  
  input:focus {
    outline: none;
    border-color: #647acb;
    box-shadow: 0 0 0 2px rgba(100, 122, 203, 0.2);
  }
  
  .btn {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    text-align: center;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    margin-top: 0.5rem;
  }
  
  .btn-primary {
    background-color: #647acb;
    color: white;
  }
  
  .btn-primary:hover {
    background-color: #536bb6;
  }
  
  .btn-secondary {
    background-color: #d9e2ec;
    color: #486581;
  }
  
  .btn-secondary:hover {
    background-color: #cbd2d9;
  }
  
  .btn-danger {
    background-color: #e12d39;
    color: white;
  }
  
  .btn-danger:hover {
    background-color: #cd1d27;
  }
  
  .form-switch {
    margin-top: 1.5rem;
    text-align: center;
    color: #64748b;
  }
  
  .link-button {
    background: none;
    border: none;
    padding: 0;
    color: #647acb;
    font-weight: 500;
    cursor: pointer;
    text-decoration: underline;
  }
  
  .link-button:hover {
    color: #536bb6;
  }
  
  .alert {
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .alert-error {
    background-color: #feebed;
    color: #e12d39;
  }
  
  .alert-success {
    background-color: #e6f7ed;
    color: #0a7a4d;
  }
  
  .loading {
    text-align: center;
    color: #64748b;
    font-style: italic;
    padding: 1rem;
  }
  
  .dashboard {
    text-align: center;
  }
  
  .user-info {
    background-color: #f8fafc;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
  }
  
  .dashboard-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .form-buttons {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
  }
  
  .form-buttons .btn {
    width: 50%;
  }
</style>
