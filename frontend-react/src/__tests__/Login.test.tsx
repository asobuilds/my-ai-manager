import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginPage from "@/app/page";

// Mock axios
jest.mock("@/lib/api", () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

describe("LoginPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the welcome text and sign-in button", () => {
    render(<LoginPage />);
    expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("shows email and password fields", () => {
    render(<LoginPage />);
    expect(screen.getByPlaceholderText(/you@example.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeInTheDocument();
  });

  it("submits the form and calls the login API on success", async () => {
    const api = (await import("@/lib/api")).default as unknown as { post: jest.Mock };
    api.post.mockResolvedValue({ data: { access_token: "fake-token" } });

    render(<LoginPage />);
    await userEvent.type(screen.getByPlaceholderText(/you@example.com/i), "test@example.com");
    await userEvent.type(screen.getByPlaceholderText(/••••••••/i), "password123");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(api.post).toHaveBeenCalledWith("/auth/login", {
      email: "test@example.com",
      password: "password123",
    });
  });
});
