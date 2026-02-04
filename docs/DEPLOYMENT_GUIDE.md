# Deployment Guide: Silver Land Properties 🚀

This guide outlines the steps to deploy your **Gold Standard** property assistant to **Render** (Backend) and **Vercel** (Frontend).

---

## 🏗️ 1. Render (Backend + Database)
Render will host your Django API and PostgreSQL database using the `render.yaml` Blueprint already in the repo.

1.  **Preparation**: Push your latest code to your GitHub repository.
2.  **Dashboard**: Go to [dashboard.render.com](https://dashboard.render.com).
3.  **New Blueprint**: Click **New** -> **Blueprint**.
4.  **Connect Repo**: Select your `proplens_assesment` repository.
5.  **Apply**: Render will detect `render.yaml`. Click **Apply**. This will create:
    -   `silver-land-api` (Web Service)
    -   `silver-land-db` (Postgres Database)
6.  **Environment Variables**: In the `silver-land-api` service settings, add these manually:
    -   `OPENAI_API_KEY`: Your OpenAI key.
    -   `TAVILY_API_KEY`: Your Tavily key.
    -   `CORS_ALLOWED_ORIGINS`: Set to your Vercel URL (get this in Step 2).
7.  **Verify**: Once deployed, check the logs. You should see the **Ultra-Robust Parser** importing property data!

---

## ⚡ 2. Vercel (Frontend)
Vercel will host your React frontend and proxy requests to Render.

1.  **New Project**: Go to [vercel.com](https://vercel.com) and click **Add New** -> **Project**.
2.  **Connect Repo**: Select the same repository.
3.  **Configure**:
    -   **Root Directory**: Set this to `frontend`.
    -   **Framework Preset**: Vite (should be auto-detected).
4.  **Environment Variables**: Add the following:
    -   `VITE_API_BASE_URL`: Your Render URL (e.g., `https://silver-land-api.onrender.com/api/v1`).
5.  **Deploy**: Click **Deploy**.

---

## 🔗 3. Connecting the Two
Once both are deployed, you need to do a final "Handshake":

1.  **Vercel URL**: Copy your live Vercel URL (e.g., `https://proplens-assesment.vercel.app`).
2.  **Render Config**: Go back to Render -> `silver-land-api` -> **Environment**.
3.  **Update CORS**: Set `CORS_ALLOWED_ORIGINS` to your Vercel URL.
4.  **Update ALLOWED_HOSTS**: Add your Render domain (e.g., `silver-land-api.onrender.com`).

---

## � 4. Admin Access (For Hiring Managers)
To show the hiring manager the **"Success Bookings"** or **"Lead Data"**, you need to create a Superuser on Render.

1.  **Open Shell**: In the Render Dashboard, go to your `silver-land-api` service and click on the **"Shell"** tab.
2.  **Create Superuser**: Run the following command:
    ```bash
    cd src && python manage.py createsuperuser
    ```
3.  **Follow Prompts**: Enter a username, email, and password.
4.  **Login**: Go to `https://your-render-backend-url.onrender.com/admin` and log in with those credentials.
5.  **Demo**: Show them the **Leads** and **Bookings** tables—they will be populated as you interact with the AI assistant!

---

## �🔥 5. Final Smoke Test (Live)
1.  Open your Vercel URL.
2.  Ask: *"Show me 3-bedroom apartments in Chicago."*
3.  Verify the map markers pop up and the AI response is accurate!

*"Your project is now truly production-ready. Good luck with the submission!"* 🏛️🎉
