const typedText = document.getElementById("typed-text");
const loader = document.getElementById("page-loader");
const navToggle = document.getElementById("nav-toggle");
const navMenu = document.getElementById("nav-menu");

const typingWords = [
    "Data Analyst",
    "Machine Learning Enthusiast",
    "Power BI Dashboard Builder",
    "Flask Project Developer",
];

let wordIndex = 0;
let charIndex = 0;
let deleting = false;

function runTypingAnimation() {
    if (!typedText) {
        return;
    }

    const currentWord = typingWords[wordIndex];
    typedText.textContent = deleting
        ? currentWord.slice(0, charIndex--)
        : currentWord.slice(0, charIndex++);

    let timeout = deleting ? 50 : 90;

    if (!deleting && charIndex === currentWord.length + 1) {
        deleting = true;
        timeout = 1200;
    } else if (deleting && charIndex === -1) {
        deleting = false;
        wordIndex = (wordIndex + 1) % typingWords.length;
        charIndex = 0;
        timeout = 250;
    }

    window.setTimeout(runTypingAnimation, timeout);
}

function revealOnScroll() {
    const revealItems = document.querySelectorAll(".reveal");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("visible");

                if (entry.target.classList.contains("skill-card")) {
                    entry.target.classList.add("in-view");
                }

                observer.unobserve(entry.target);
            });
        },
        { threshold: 0.18 }
    );

    revealItems.forEach((item) => observer.observe(item));
}

function enableMobileNav() {
    if (!navToggle || !navMenu) {
        return;
    }

    navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("open");
    });

    navMenu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => navMenu.classList.remove("open"));
    });
}

function setActiveNavLink() {
    const sections = document.querySelectorAll("main section[id]");
    const navLinks = document.querySelectorAll(".nav-links a");

    if (!sections.length || !navLinks.length || window.location.pathname !== "/") {
        return;
    }

    window.addEventListener("scroll", () => {
        const scrollY = window.scrollY + 140;

        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute("id");

            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                navLinks.forEach((link) => {
                    link.classList.toggle("active", link.getAttribute("href") === `#${sectionId}`);
                });
            }
        });
    });
}

function enableDeleteConfirmation() {
    document.querySelectorAll(".js-confirm-delete").forEach((button) => {
        button.addEventListener("click", (event) => {
            const confirmed = window.confirm("Are you sure you want to delete this item?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

const projectSearch = document.getElementById("project-search");
const projectFilterButtons = document.querySelectorAll(".filter-button");
const projectCards = document.querySelectorAll(".project-card");

function filterProjects() {
    const query = projectSearch?.value.trim().toLowerCase() || "";
    const activeButton = document.querySelector(".filter-button.active");
    const activeFilter = activeButton?.dataset.filter || "all";

    projectCards.forEach((card) => {
        const searchText = card.dataset.searchText?.toLowerCase() || "";
        const tags = card.dataset.tags?.toLowerCase() || "";
        const matchesQuery = !query || searchText.includes(query);
        const matchesFilter = activeFilter === "all" || tags.includes(activeFilter);
        card.classList.toggle("hidden", !(matchesQuery && matchesFilter));
    });
}

function enableProjectFilters() {
    if (!projectSearch || !projectFilterButtons.length || !projectCards.length) {
        return;
    }

    projectSearch.addEventListener("input", filterProjects);
    projectFilterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            projectFilterButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            filterProjects();
        });
    });
}

function enableCaseStudyToggles() {
    document.querySelectorAll(".case-study-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-target");
            const panel = document.getElementById(targetId);
            if (!panel) {
                return;
            }

            panel.classList.toggle("open");
            button.textContent = panel.classList.contains("open") ? "Hide Case Study" : "View Case Study";
        });
    });
}

window.addEventListener("load", () => {
    loader?.classList.add("hidden");
});

runTypingAnimation();
revealOnScroll();
enableMobileNav();
setActiveNavLink();
enableDeleteConfirmation();
enableCaseStudyToggles();
enableProjectFilters();
