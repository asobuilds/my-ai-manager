import "@testing-library/jest-dom";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import JobsPage from "@/app/dashboard/jobs/page";

// Mock axios
jest.mock("@/lib/api", () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    patch: jest.fn(),
  },
}));

const api = jest.requireMock("@/lib/api").default as {
  get: jest.Mock;
  post: jest.Mock;
  patch: jest.Mock;
};

describe("JobsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("shows loading skeletons while fetching", async () => {
    api.get.mockReturnValue(new Promise(() => {})); // never resolves
    render(<JobsPage />);
    expect(screen.getByText(/💼 Job Tracker/i)).toBeInTheDocument();
    expect(screen.getByText(/New Application/i)).toBeInTheDocument();
    // Skeleton placeholders should be visible
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders all four Kanban columns when jobs are loaded", async () => {
    const jobs = [
      { id: "1", company_name: "Google", job_title: "SWE", status: "applied" },
      { id: "2", company_name: "Meta", job_title: "PM", status: "interviewing" },
      { id: "3", company_name: "Stripe", job_title: "DES", status: "offered" },
      { id: "4", company_name: "Netflix", job_title: "ENG", status: "rejected" },
    ];
    api.get.mockResolvedValue({ data: jobs });

    render(<JobsPage />);

    await waitFor(() => {
      // Column headers are h2 elements — one per column
      const headers = screen.getAllByRole("heading", { level: 2 });
      expect(headers).toHaveLength(4);
      expect(headers[0]).toHaveTextContent("Applied");
      expect(headers[1]).toHaveTextContent("Interviewing");
      expect(headers[2]).toHaveTextContent("Offered");
      expect(headers[3]).toHaveTextContent("Rejected");
    });

    // Verify job cards are visible
    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByText("Meta")).toBeInTheDocument();
    expect(screen.getByText("Stripe")).toBeInTheDocument();
    expect(screen.getByText("Netflix")).toBeInTheDocument();
  });

  it("shows empty state in each column when no jobs exist", async () => {
    api.get.mockResolvedValue({ data: [] });

    render(<JobsPage />);

    await waitFor(() => {
      // All four empty-state messages should appear
      const emptyStates = screen.getAllByText("No applications");
      expect(emptyStates).toHaveLength(4);
    });
  });

  it("calls GET /jobs on mount", async () => {
    api.get.mockResolvedValue({ data: [] });
    render(<JobsPage />);
    expect(api.get).toHaveBeenCalledWith("/jobs");
  });

  it("updates job status via PATCH when dropdown changes", async () => {
    const jobs = [
      { id: "1", company_name: "Google", job_title: "SWE", status: "applied" },
    ];
    api.get.mockResolvedValue({ data: jobs });
    api.patch.mockResolvedValue({});
    render(<JobsPage />);

    await waitFor(() => expect(screen.getByText("Google")).toBeInTheDocument());

    const select = screen.getByRole("combobox");
    await userEvent.selectOptions(select, "interviewing");

    expect(api.patch).toHaveBeenCalledWith("/jobs/1", { status: "interviewing" });
  });
});
