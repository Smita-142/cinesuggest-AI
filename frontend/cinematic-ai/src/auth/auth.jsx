const USER_KEY = "cinematchUser";
const AUTH_KEY = "cinematchAuth";

export const isValidEmail = (email) => {
  const gmailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
  return gmailRegex.test(email);
};

export const isStrongPassword = (password) => {
  const passwordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

  return passwordRegex.test(password);
};

export const registerUser = (userData) => {
  const existingUser = JSON.parse(localStorage.getItem(USER_KEY));

  if (existingUser) {
    return {
      success: false,
      message: "An account already exists. Please login.",
    };
  }

  localStorage.setItem(USER_KEY, JSON.stringify(userData));

  return {
    success: true,
    message: "Account created successfully.",
  };
};

export const loginUser = (email, password) => {
  const user = JSON.parse(localStorage.getItem(USER_KEY));

  if (!user) {
    return {
      success: false,
      message: "No account found. Please create an account first.",
    };
  }

  if (user.email !== email) {
    return {
      success: false,
      message: "Email not registered.",
    };
  }

  if (user.password !== password) {
    return {
      success: false,
      message: "Incorrect password.",
    };
  }

  localStorage.setItem(AUTH_KEY, "true");

  return {
    success: true,
    user,
  };
};

export const logoutUser = () => {
  localStorage.removeItem(AUTH_KEY);
};

export const isLoggedIn = () => {
  return localStorage.getItem(AUTH_KEY) === "true";
};

export const getCurrentUser = () => {
  return JSON.parse(localStorage.getItem(USER_KEY));
};