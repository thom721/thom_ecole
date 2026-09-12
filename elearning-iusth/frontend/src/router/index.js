import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const LoginView = () => import('@/views/auth/LoginView.vue')
const ForgotPasswordView = () => import('@/views/auth/ForgotPasswordView.vue')
const ResetPasswordView = () => import('@/views/auth/ResetPasswordView.vue')
const ChangePasswordView = () => import('@/views/auth/ChangePasswordView.vue')

const StudentLayout = () => import('@/layouts/StudentLayout.vue')
const StudentCourseListView = () => import('@/views/student/CourseListView.vue')
const StudentCourseDetailView = () => import('@/views/student/CourseDetailView.vue')
const StudentAssignmentSubmitView = () => import('@/views/student/AssignmentSubmitView.vue')
const StudentQuizTakeView = () => import('@/views/student/QuizTakeView.vue')
const StudentGradesView = () => import('@/views/student/GradesView.vue')
const StudentLessonTakeView = () => import('@/views/student/LessonTakeView.vue')
const StudentWorkshopView = () => import('@/views/student/WorkshopView.vue')
const StudentWorkshopAssessView = () => import('@/views/student/WorkshopAssessView.vue')
const MessagingView = () => import('@/views/MessagingView.vue')
const StudentMyBadgesView = () => import('@/views/student/MyBadgesView.vue')
const TeacherBadgesView = () => import('@/views/teacher/BadgesView.vue')
const AdminCompetencyFrameworksView = () => import('@/views/admin/CompetencyFrameworksView.vue')
const TeacherCourseCompetenciesView = () => import('@/views/teacher/CourseCompetenciesView.vue')
const StudentMyCompetenciesView = () => import('@/views/student/MyCompetenciesView.vue')
const PlansView = () => import('@/views/PlansView.vue')
const DashboardView = () => import('@/views/DashboardView.vue')

const TeacherLayout = () => import('@/layouts/TeacherLayout.vue')
const TeacherCourseListView = () => import('@/views/teacher/CourseListView.vue')
const TeacherCourseDetailView = () => import('@/views/teacher/CourseDetailView.vue')
const TeacherAssignmentGradingView = () => import('@/views/teacher/AssignmentGradingView.vue')
const TeacherQuizBuilderView = () => import('@/views/teacher/QuizBuilderView.vue')
const TeacherQuizGradingView = () => import('@/views/teacher/QuizGradingView.vue')
const TeacherGradebookView = () => import('@/views/teacher/GradebookView.vue')
const TeacherCompletionReportView = () => import('@/views/teacher/CompletionReportView.vue')
const TeacherAccessLogView = () => import('@/views/teacher/AccessLogView.vue')
const TeacherCourseImportView = () => import('@/views/teacher/CourseImportView.vue')
const TeacherGroupsView = () => import('@/views/teacher/GroupsView.vue')
const TeacherActivityAccessView = () => import('@/views/teacher/ActivityAccessView.vue')
const TeacherScalesView = () => import('@/views/teacher/ScalesView.vue')
const TeacherLessonBuilderView = () => import('@/views/teacher/LessonBuilderView.vue')
const TeacherLessonGradingView = () => import('@/views/teacher/LessonGradingView.vue')
const TeacherWorkshopBuilderView = () => import('@/views/teacher/WorkshopBuilderView.vue')
const TeacherWorkshopGradingView = () => import('@/views/teacher/WorkshopGradingView.vue')

const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const AdminCourseListView = () => import('@/views/admin/CourseListView.vue')
const AdminCategoryListView = () => import('@/views/admin/CategoryListView.vue')
const AdminUserListView = () => import('@/views/admin/UserListView.vue')
const AdminIntegrationImportView = () => import('@/views/admin/IntegrationImportView.vue')
const AdminStudentActivationView = () => import('@/views/admin/StudentActivationView.vue')
const AdminCohortsView = () => import('@/views/admin/CohortsView.vue')

const LiveSessionView = () => import('@/views/LiveSessionView.vue')
const TeacherLiveSessionAttendanceView = () => import('@/views/teacher/LiveSessionAttendanceView.vue')

const TeacherInteractiveVideoBuilderView = () => import('@/views/teacher/InteractiveVideoBuilderView.vue')
const TeacherInteractiveVideoGradingView = () => import('@/views/teacher/InteractiveVideoGradingView.vue')
const StudentInteractiveVideoTakeView = () => import('@/views/student/InteractiveVideoTakeView.vue')

const StaffMeetingView = () => import('@/views/StaffMeetingView.vue')
const AdminStaffMeetingsView = () => import('@/views/admin/StaffMeetingsView.vue')
const StaffLayout = () => import('@/layouts/StaffLayout.vue')
const AdminRolesView = () => import('@/views/admin/RolesView.vue')

const ForumView = () => import('@/views/ForumView.vue')
const ForumDiscussionView = () => import('@/views/ForumDiscussionView.vue')
const ChoiceView = () => import('@/views/ChoiceView.vue')
const GlossaryView = () => import('@/views/GlossaryView.vue')
const GlossaryEntryView = () => import('@/views/GlossaryEntryView.vue')
const WikiView = () => import('@/views/WikiView.vue')
const WikiPageView = () => import('@/views/WikiPageView.vue')
const WikiNewPageView = () => import('@/views/WikiNewPageView.vue')
const WikiHistoryView = () => import('@/views/WikiHistoryView.vue')
const CalendarView = () => import('@/views/CalendarView.vue')
const EnrollView = () => import('@/views/EnrollView.vue')

const NotFound = () => import('@/views/NotFound.vue')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
  { path: '/reset-password', name: 'reset-password', component: ResetPasswordView },
  { path: '/change-password', name: 'change-password', component: ChangePasswordView, meta: { requiresAuth: true } },
  { path: '/enroll/:courseId', name: 'enroll', component: EnrollView, meta: { requiresAuth: true } },

  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '', redirect: '/student/courses' },
      { path: 'courses', name: 'student-courses', component: StudentCourseListView },
      { path: 'courses/:id', name: 'student-course-detail', component: StudentCourseDetailView },
      { path: 'assignments/:id', name: 'student-assignment-submit', component: StudentAssignmentSubmitView },
      { path: 'quizzes/:id', name: 'student-quiz-take', component: StudentQuizTakeView },
      { path: 'courses/:id/grades', name: 'student-grades', component: StudentGradesView },
      { path: 'calendar', name: 'student-calendar', component: CalendarView },
      { path: 'live-sessions/:id', name: 'student-live-session', component: LiveSessionView },
      { path: 'interactive-videos/:id', name: 'student-interactive-video', component: StudentInteractiveVideoTakeView },
      { path: 'forums/:id', name: 'student-forum', component: ForumView },
      { path: 'forum-discussions/:id', name: 'student-forum-discussion', component: ForumDiscussionView },
      { path: 'choices/:id', name: 'student-choice', component: ChoiceView },
      { path: 'glossaries/:id', name: 'student-glossary', component: GlossaryView },
      { path: 'glossary-entries/:id', name: 'student-glossary-entry', component: GlossaryEntryView },
      { path: 'wikis/:id', name: 'student-wiki', component: WikiView },
      { path: 'wiki-pages/new', name: 'student-wiki-new-page', component: WikiNewPageView },
      { path: 'wiki-pages/:id/history', name: 'student-wiki-history', component: WikiHistoryView },
      { path: 'wiki-pages/:id', name: 'student-wiki-page', component: WikiPageView },
      { path: 'lessons/:id', name: 'student-lesson-take', component: StudentLessonTakeView },
      { path: 'workshops/:id', name: 'student-workshop', component: StudentWorkshopView },
      { path: 'workshop-assessments/:id', name: 'student-workshop-assess', component: StudentWorkshopAssessView },
      { path: 'messages', name: 'student-messages', component: MessagingView },
      { path: 'badges', name: 'student-badges', component: StudentMyBadgesView },
      { path: 'competencies', name: 'student-competencies', component: StudentMyCompetenciesView },
      { path: 'plans', name: 'student-plans', component: PlansView },
      { path: 'dashboard', name: 'student-dashboard', component: DashboardView },
    ],
  },

  {
    path: '/teacher',
    component: TeacherLayout,
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '', redirect: '/teacher/courses' },
      { path: 'courses', name: 'teacher-courses', component: TeacherCourseListView },
      { path: 'courses/:id', name: 'teacher-course-detail', component: TeacherCourseDetailView },
      { path: 'assignments/:id', name: 'teacher-assignment-grading', component: TeacherAssignmentGradingView },
      { path: 'quizzes/:id', name: 'teacher-quiz-builder', component: TeacherQuizBuilderView },
      { path: 'quizzes/:id/attempts', name: 'teacher-quiz-grading', component: TeacherQuizGradingView },
      { path: 'courses/:id/gradebook', name: 'teacher-gradebook', component: TeacherGradebookView },
      { path: 'courses/:id/groups', name: 'teacher-groups', component: TeacherGroupsView },
      { path: 'access/:itemType/:itemId', name: 'teacher-activity-access', component: TeacherActivityAccessView },
      { path: 'courses/:id/scales', name: 'teacher-scales', component: TeacherScalesView },
      { path: 'calendar', name: 'teacher-calendar', component: CalendarView },
      { path: 'live-sessions/:id', name: 'teacher-live-session', component: LiveSessionView },
      { path: 'live-sessions/:id/attendance', name: 'teacher-live-session-attendance', component: TeacherLiveSessionAttendanceView },
      { path: 'interactive-videos/:id', name: 'teacher-interactive-video', component: TeacherInteractiveVideoBuilderView },
      { path: 'interactive-videos/:id/grading', name: 'teacher-interactive-video-grading', component: TeacherInteractiveVideoGradingView },
      { path: 'forums/:id', name: 'teacher-forum', component: ForumView },
      { path: 'forum-discussions/:id', name: 'teacher-forum-discussion', component: ForumDiscussionView },
      { path: 'choices/:id', name: 'teacher-choice', component: ChoiceView },
      { path: 'glossaries/:id', name: 'teacher-glossary', component: GlossaryView },
      { path: 'glossary-entries/:id', name: 'teacher-glossary-entry', component: GlossaryEntryView },
      { path: 'wikis/:id', name: 'teacher-wiki', component: WikiView },
      { path: 'wiki-pages/new', name: 'teacher-wiki-new-page', component: WikiNewPageView },
      { path: 'wiki-pages/:id/history', name: 'teacher-wiki-history', component: WikiHistoryView },
      { path: 'wiki-pages/:id', name: 'teacher-wiki-page', component: WikiPageView },
      { path: 'courses/:id/completion', name: 'teacher-completion-report', component: TeacherCompletionReportView },
      { path: 'courses/:id/access-log', name: 'teacher-access-log', component: TeacherAccessLogView },
      { path: 'courses/import', name: 'teacher-course-import', component: TeacherCourseImportView },
      { path: 'lessons/:id', name: 'teacher-lesson-builder', component: TeacherLessonBuilderView },
      { path: 'lessons/:id/grading', name: 'teacher-lesson-grading', component: TeacherLessonGradingView },
      { path: 'workshops/:id', name: 'teacher-workshop-builder', component: TeacherWorkshopBuilderView },
      { path: 'workshops/:id/grading', name: 'teacher-workshop-grading', component: TeacherWorkshopGradingView },
      { path: 'messages', name: 'teacher-messages', component: MessagingView },
      { path: 'staff-meetings', name: 'teacher-staff-meetings', component: AdminStaffMeetingsView },
      { path: 'staff-meetings/:id', name: 'teacher-staff-meeting', component: StaffMeetingView },
      { path: 'courses/:id/badges', name: 'teacher-badges', component: TeacherBadgesView },
      { path: 'courses/:id/competencies', name: 'teacher-competencies', component: TeacherCourseCompetenciesView },
      { path: 'plans', name: 'teacher-plans', component: PlansView },
      { path: 'dashboard', name: 'teacher-dashboard', component: DashboardView },
    ],
  },

  {
    path: '/staff',
    component: StaffLayout,
    meta: { requiresAuth: true, role: 'staff' },
    children: [
      { path: '', redirect: '/staff/staff-meetings' },
      { path: 'messages', name: 'staff-messages', component: MessagingView },
      { path: 'staff-meetings', name: 'staff-staff-meetings', component: AdminStaffMeetingsView },
      { path: 'staff-meetings/:id', name: 'staff-staff-meeting', component: StaffMeetingView },
    ],
  },

  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/courses' },
      { path: 'courses', name: 'admin-courses', component: AdminCourseListView },
      { path: 'categories', name: 'admin-categories', component: AdminCategoryListView },
      { path: 'users', name: 'admin-users', component: AdminUserListView },
      { path: 'integration-import', name: 'admin-integration-import', component: AdminIntegrationImportView },
      { path: 'student-activation', name: 'admin-student-activation', component: AdminStudentActivationView },
      { path: 'cohorts', name: 'admin-cohorts', component: AdminCohortsView },
      { path: 'messages', name: 'admin-messages', component: MessagingView },
      { path: 'staff-meetings', name: 'admin-staff-meetings', component: AdminStaffMeetingsView },
      { path: 'staff-meetings/:id', name: 'admin-staff-meeting', component: StaffMeetingView },
      { path: 'roles', name: 'admin-roles', component: AdminRolesView },
      { path: 'competency-frameworks', name: 'admin-competency-frameworks', component: AdminCompetencyFrameworksView },
      { path: 'plans', name: 'admin-plans', component: PlansView },
    ],
  },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!to.meta.requiresAuth) return true

  if (!auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  // Compte auto-provisionné (import ecole_nginx) avec mot de passe
  // temporaire — bloque toute navigation ailleurs tant qu'il n'est pas
  // changé (voir plan "Provisionnement automatique des comptes professeur").
  if (auth.user?.must_change_password && to.name !== 'change-password') {
    return { name: 'change-password' }
  }

  // Un admin a accès à toutes les zones (y compris /teacher/* pour gérer un
  // cours) — voir require_course_role côté backend qui applique la même
  // règle de contournement.
  if (auth.isAdmin) return true

  if (to.meta.role && auth.user?.system_role !== to.meta.role) {
    return { name: 'login' }
  }

  return true
})

export default router
