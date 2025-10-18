function openLogin() {
  document.getElementById("loginModal").style.display = "flex";
}

function closeLogin() {
  document.getElementById("loginModal").style.display = "none";
}

function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const msg = document.getElementById("loginMsg");

  // Hardcoded login credentials
  const users = [
    { username: "admin", password: "12345" },
    { username: "student", password: "abcde" }
  ];

  const user = users.find(
    (u) => u.username === username && u.password === password
  );

  if (user) {
    msg.textContent = "✅ Login Successful! Redirecting...";
    msg.style.color = "green";
    setTimeout(() => {
      alert("Welcome " + username + "!");
      closeLogin();
    }, 1000);
  } else {
    msg.textContent = "❌ Invalid Username or Password";
    msg.style.color = "red";
  }
}