<template>
  <div v-if="course">
    <router-link to="/teacher/courses" class="text-sm text-gray-500 hover:underline">{{ t('common.backToMyCourses') }}</router-link>
    <div class="flex items-center justify-between mt-2 mb-6">
      <div>
        <h1 class="text-lg font-bold text-gray-900">{{ course.full_name }}</h1>
        <p v-if="categoryName" class="text-xs text-gray-500 mt-0.5">{{ t('teacher.courseDetail.faculty') }} : {{ categoryName }}</p>
      </div>
      <div class="flex gap-3 flex-wrap">
        <router-link :to="`/teacher/courses/${course.id}/gradebook`" class="text-sm text-blue-600 hover:underline">{{ t('teacher.courseDetail.gradebook') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/groups`" class="text-sm text-blue-600 hover:underline">{{ t('groups.navLink') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/scales`" class="text-sm text-blue-600 hover:underline">{{ t('scales.navLink') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/badges`" class="text-sm text-blue-600 hover:underline">{{ t('badges.navLink') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/competencies`" class="text-sm text-blue-600 hover:underline">{{ t('competency.navLink') }}</router-link>
        <router-link :to="`/teacher/calendar?course_id=${course.id}`" class="text-sm text-blue-600 hover:underline">{{ t('teacher.courseDetail.calendar') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/completion`" class="text-sm text-blue-600 hover:underline">{{ t('teacher.courseDetail.completion') }}</router-link>
        <router-link :to="`/teacher/courses/${course.id}/access-log`" class="text-sm text-blue-600 hover:underline">{{ t('teacher.courseDetail.accessLog') }}</router-link>
        <label class="text-xs text-gray-500 flex items-center gap-1">
          <input type="checkbox" v-model="exportWithStudentData" />{{ t('courseExport.includeStudentData') }}
        </label>
        <button class="text-sm text-blue-600 hover:underline" @click="onExport">{{ t('teacher.courseDetail.export') }}</button>
      </div>
    </div>

    <!-- Format du cours -->
    <details class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('courseFormat.settingsTitle') }}</summary>
      <div class="grid grid-cols-2 gap-3 mt-3">
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('courseFormat.formatLabel') }}</label>
          <select v-model="formatSettings.format" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="topics">{{ t('courseFormat.format.topics') }}</option>
            <option value="weeks">{{ t('courseFormat.format.weeks') }}</option>
            <option value="social">{{ t('courseFormat.format.social') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('courseFormat.displayLabel') }}</label>
          <select v-model="formatSettings.course_display" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="single_page">{{ t('courseFormat.display.single_page') }}</option>
            <option value="paginated">{{ t('courseFormat.display.paginated') }}</option>
          </select>
        </div>
      </div>
      <div v-if="formatSettings.format === 'social'" class="mt-3">
        <label class="block text-xs text-gray-600 mb-1">{{ t('courseFormat.socialForumLabel') }}</label>
        <select v-model="formatSettings.social_forum_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">{{ t('courseFormat.chooseForum') }}</option>
          <option v-for="f in allForums" :key="f.id" :value="f.id">{{ f.title }}</option>
        </select>
      </div>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold mt-3" @click="onSaveFormat">{{ t('common.save') }}</button>
    </details>

    <!-- Inscriptions -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('teacher.courseDetail.enrolledStudents') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="e in enrollments" :key="e.id" class="flex items-center justify-between py-1">
          <span>{{ e.user_name || e.user_id }} — {{ e.role_in_course }}
            <span class="text-gray-400">({{ e.method || 'manual' }}<template v-if="e.status !== 'active'">, {{ e.status }}</template>)</span>
          </span>
          <button class="text-red-600 text-xs" @click="onUnenroll(e.id)">{{ t('teacher.courseDetail.unenroll') }}</button>
        </li>
      </ul>
      <div class="flex gap-2">
        <input v-model="enrollEmail" :placeholder="t('teacher.courseDetail.enrollEmailPlaceholder')"
          class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onEnroll">
          {{ t('teacher.courseDetail.enroll') }}
        </button>
      </div>
      <p v-if="enrollMessage" class="text-xs text-red-600 mt-2">{{ enrollMessage }}</p>
    </div>

    <!-- Méthodes d'inscription -->
    <div v-if="enrollmentSettings" class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('enroll.methodsTitle') }}</h2>

      <label class="flex items-center gap-2 text-sm mb-1">
        <input type="checkbox" v-model="enrollmentSettings.self_enrollment_enabled" @change="onSaveEnrollmentSettings" />
        {{ t('enroll.selfEnrollEnabled') }}
      </label>
      <input v-if="enrollmentSettings.self_enrollment_enabled" v-model="enrollmentSettings.self_enrollment_key"
        @blur="onSaveEnrollmentSettings" :placeholder="t('enroll.keyOptionalPlaceholder')"
        class="border border-gray-300 rounded-lg px-2 py-1 text-xs mb-3 ml-6" />

      <label class="flex items-center gap-2 text-sm mb-1">
        <input type="checkbox" v-model="enrollmentSettings.guest_access_enabled" @change="onSaveEnrollmentSettings" />
        {{ t('enroll.guestEnabled') }}
      </label>
      <input v-if="enrollmentSettings.guest_access_enabled" v-model="enrollmentSettings.guest_access_key"
        @blur="onSaveEnrollmentSettings" :placeholder="t('enroll.keyOptionalPlaceholder')"
        class="border border-gray-300 rounded-lg px-2 py-1 text-xs mb-3 ml-6" />

      <h3 class="text-xs font-semibold text-gray-600 mt-3 mb-1">{{ t('enroll.cohortSyncs') }}</h3>
      <ul class="text-sm mb-2">
        <li v-for="s in cohortSyncs" :key="s.id" class="flex items-center justify-between py-1">
          <span>{{ s.cohort_name }} — {{ s.role }}</span>
          <button class="text-red-600 text-xs" @click="onRemoveCohortSync(s.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
      <div class="flex gap-2">
        <select v-model="selectedCohortId" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1">
          <option value="">{{ t('enroll.chooseCohort') }}</option>
          <option v-for="c in allCohorts" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <button class="bg-gray-100 rounded-lg px-2 py-1 text-xs" @click="onAddCohortSync">{{ t('common.add') }}</button>
      </div>
    </div>

    <!-- Format social : le forum désigné remplace la grille de sections -->
    <div v-if="course.format === 'social'" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <router-link v-if="course.social_forum" :to="`/teacher/forums/${course.social_forum.id}`"
        class="text-blue-600 hover:underline font-semibold">
        💬 {{ course.social_forum.title }} — {{ t('courseFormat.openForum') }}
      </router-link>
      <p v-else class="text-sm text-gray-500">{{ t('courseFormat.noSocialForum') }}</p>
    </div>

    <div v-else>
      <div v-if="course.course_display === 'paginated' && course.sections.length" class="flex items-center justify-between mb-3 text-sm">
        <button class="text-blue-600 disabled:opacity-30" :disabled="pageIndex === 0" @click="pageIndex--">{{ t('admin.courses.prevPage') }}</button>
        <span class="text-gray-500">{{ course.sections[pageIndex]?.title || t('common.section') }}</span>
        <button class="text-blue-600 disabled:opacity-30" :disabled="pageIndex >= course.sections.length - 1" @click="pageIndex++">{{ t('admin.courses.nextPage') }}</button>
      </div>

    <!-- Sections -->
    <div v-for="section in displayedSections" :key="section.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-1">{{ section.title || t('common.section') }}</h2>
      <p v-if="section.week_start" class="text-xs text-gray-400 mb-2">{{ t('courseFormat.weekRange', { start: formatDate(section.week_start), end: formatDate(section.week_end) }) }}</p>

      <div class="grid gap-2 mb-3">
        <div v-for="r in section.resources" :key="r.id" class="bg-gray-50 rounded-lg p-2 text-sm flex items-center justify-between">
          <span>📎 {{ r.title }}</span>
          <router-link :to="`/teacher/access/resource/${r.id}?title=${encodeURIComponent(r.title)}&courseId=${course.id}`" class="text-gray-400 text-xs hover:text-gray-700">⚙️</router-link>
        </div>
        <div v-for="a in section.assignments" :key="a.id" class="bg-amber-50 rounded-lg p-2 text-sm flex items-center justify-between">
          <span>📄 {{ a.title }} ({{ a.max_points }} {{ t('common.pts') }})</span>
          <router-link :to="`/teacher/assignments/${a.id}`" class="text-blue-600 text-xs hover:underline">{{ t('teacher.courseDetail.grade') }}</router-link>
        </div>
        <router-link v-for="q in section.quizzes" :key="q.id" :to="`/teacher/quizzes/${q.id}`"
          class="bg-purple-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-purple-100">
          <span>📝 {{ q.title }}</span>
          <span class="text-purple-600 text-xs">{{ t('teacher.courseDetail.manage') }}</span>
        </router-link>
        <div v-for="f in section.forums" :key="f.id" class="bg-blue-50 rounded-lg p-2 text-sm flex items-center justify-between">
          <router-link :to="`/teacher/forums/${f.id}`" class="no-underline text-inherit hover:underline">💬 {{ f.title }}</router-link>
          <router-link :to="`/teacher/access/forum/${f.id}?title=${encodeURIComponent(f.title)}&courseId=${course.id}`" class="text-gray-400 text-xs hover:text-gray-700">⚙️</router-link>
        </div>
        <div v-for="c in section.choices" :key="c.id" class="bg-teal-50 rounded-lg p-2 text-sm flex items-center justify-between">
          <router-link :to="`/teacher/choices/${c.id}`" class="no-underline text-inherit hover:underline">🗳️ {{ c.title }}</router-link>
          <router-link :to="`/teacher/access/choice/${c.id}?title=${encodeURIComponent(c.title)}&courseId=${course.id}`" class="text-gray-400 text-xs hover:text-gray-700">⚙️</router-link>
        </div>
        <router-link v-for="g in section.glossaries" :key="g.id" :to="`/teacher/glossaries/${g.id}`"
          class="bg-indigo-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-indigo-100">
          <span>📖 {{ g.title }}</span>
        </router-link>
        <router-link v-for="w in section.wikis" :key="w.id" :to="`/teacher/wikis/${w.id}`"
          class="bg-cyan-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-cyan-100">
          <span>📚 {{ w.title }}</span>
        </router-link>
        <router-link v-for="l in section.lessons" :key="l.id" :to="`/teacher/lessons/${l.id}`"
          class="bg-rose-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-rose-100">
          <span>📘 {{ l.title }}</span>
        </router-link>
        <router-link v-for="w in section.workshops" :key="w.id" :to="`/teacher/workshops/${w.id}`"
          class="bg-orange-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-orange-100">
          <span>🛠️ {{ w.title }}</span>
        </router-link>
        <router-link v-for="ls in section.live_sessions" :key="ls.id" :to="`/teacher/live-sessions/${ls.id}`"
          class="bg-red-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-red-100">
          <span>🎥 {{ ls.title }}</span>
        </router-link>
        <router-link v-for="iv in section.interactive_videos" :key="iv.id" :to="`/teacher/interactive-videos/${iv.id}`"
          class="bg-cyan-50 rounded-lg p-2 text-sm flex items-center justify-between no-underline text-inherit hover:bg-cyan-100">
          <span>🎬 {{ iv.title }}</span>
        </router-link>
      </div>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('liveSession.addLiveSession') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newLiveSessionTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-model="newLiveSessionStart[section.id]" type="datetime-local" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <input v-model="newLiveSessionEnd[section.id]" type="datetime-local" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddLiveSession(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('interactiveVideo.addVideo') }}</summary>
        <div class="mt-2 flex flex-col gap-2">
          <input v-model="newVideoTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <select v-model="newVideoSourceType[section.id]" class="border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="url">{{ t('interactiveVideo.sourceUrl') }}</option>
            <option value="file">{{ t('interactiveVideo.sourceFile') }}</option>
          </select>
          <input v-if="newVideoSourceType[section.id] !== 'file'" v-model="newVideoUrl[section.id]" placeholder="https://..." class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <input v-else type="file" @change="onVideoFileChange($event, section.id)" class="text-sm" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm self-start" @click="onAddVideo(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addResource') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newResourceTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-model="newResourceContent[section.id]" :placeholder="t('teacher.courseDetail.contentPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddResource(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addAssignment') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newAssignmentTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-if="!newAssignmentScaleId[section.id]" v-model="newAssignmentPoints[section.id]" type="number" :placeholder="t('teacher.courseDetail.pointsPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          <select v-model="newAssignmentScaleId[section.id]" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-32">
            <option value="">{{ t('scales.noScale') }}</option>
            <option v-for="s in courseScales" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <label class="flex items-center gap-1 text-xs text-gray-600 whitespace-nowrap">
            <input type="checkbox" v-model="newAssignmentGroupMode[section.id]" />
            {{ t('teacher.courseDetail.groupAssignment') }}
          </label>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddAssignment(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addQuiz') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newQuizTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-model="newQuizTimeLimit[section.id]" type="number" :placeholder="t('teacher.courseDetail.quizMinutesPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-40" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddQuiz(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addForum') }}</summary>
        <div class="mt-2 space-y-2">
          <div class="flex gap-2">
            <input v-model="newForumTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddForum(section.id)">{{ t('common.add') }}</button>
          </div>
          <select v-model="newForumGroupMode[section.id]" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-xs">
            <option value="no_groups">{{ t('groups.modeNoGroups') }}</option>
            <option value="separate_groups">{{ t('groups.modeSeparate') }}</option>
            <option value="visible_groups">{{ t('groups.modeVisible') }}</option>
          </select>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addChoice') }}</summary>
        <div class="mt-2 space-y-2">
          <input v-model="newChoiceTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <input v-model="newChoiceOptionsRaw[section.id]" :placeholder="t('teacher.courseDetail.choiceOptionsPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <label class="flex items-center gap-1 text-xs text-gray-600">
            <input type="checkbox" v-model="newChoiceAllowMultiple[section.id]" /> {{ t('teacher.courseDetail.choiceAllowMultiple') }}
          </label>
          <select v-model="newChoiceGroupMode[section.id]" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-xs">
            <option value="no_groups">{{ t('groups.modeNoGroups') }}</option>
            <option value="separate_groups">{{ t('groups.modeSeparate') }}</option>
            <option value="visible_groups">{{ t('groups.modeVisible') }}</option>
          </select>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddChoice(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addGlossary') }}</summary>
        <div class="mt-2 space-y-2">
          <input v-model="newGlossaryTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <label class="flex items-center gap-1 text-xs text-gray-600">
            <input type="checkbox" v-model="newGlossaryAllowStudentEntries[section.id]" /> {{ t('teacher.courseDetail.glossaryAllowStudentEntries') }}
          </label>
          <label v-if="newGlossaryAllowStudentEntries[section.id]" class="flex items-center gap-1 text-xs text-gray-600">
            <input type="checkbox" v-model="newGlossaryRequireApproval[section.id]" /> {{ t('teacher.courseDetail.glossaryRequireApproval') }}
          </label>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddGlossary(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm">
        <summary class="cursor-pointer text-gray-600">{{ t('teacher.courseDetail.addWiki') }}</summary>
        <div class="mt-2 space-y-2">
          <input v-model="newWikiTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <select v-model="newWikiMode[section.id]" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="collaborative">{{ t('wiki.modeCollaborative') }}</option>
            <option value="individual">{{ t('wiki.modeIndividual') }}</option>
          </select>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddWiki(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mt-2">
        <summary class="cursor-pointer text-gray-600">{{ t('lesson.addLesson') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newLessonTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddLesson(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="text-sm mt-2">
        <summary class="cursor-pointer text-gray-600">{{ t('workshop.addWorkshop') }}</summary>
        <div class="mt-2 flex gap-2">
          <input v-model="newWorkshopTitle[section.id]" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <select v-model="newWorkshopStrategy[section.id]" class="border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="accumulative">{{ t('workshop.strategy.accumulative') }}</option>
            <option value="comments">{{ t('workshop.strategy.comments') }}</option>
            <option value="numerrors">{{ t('workshop.strategy.numerrors') }}</option>
            <option value="rubric">{{ t('workshop.strategy.rubric') }}</option>
          </select>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddWorkshop(section.id)">{{ t('common.add') }}</button>
        </div>
      </details>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('teacher.courseDetail.addSection') }}</summary>
      <div class="mt-3 flex gap-2">
        <input v-model="newSectionTitle" :placeholder="t('teacher.courseDetail.sectionTitlePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onAddSection">{{ t('common.add') }}</button>
      </div>
    </details>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCoursesStore } from '@/stores/courses'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useQuizzesStore } from '@/stores/quizzes'
import { useForumsStore } from '@/stores/forums'
import { useChoicesStore } from '@/stores/choices'
import { useGlossariesStore } from '@/stores/glossaries'
import { useWikisStore } from '@/stores/wikis'
import { useLessonsStore } from '@/stores/lessons'
import { useWorkshopsStore } from '@/stores/workshops'
import { useLiveSessionsStore } from '@/stores/liveSessions'
import { useInteractiveVideosStore } from '@/stores/interactiveVideos'
import { useEnrollmentMethodsStore } from '@/stores/enrollmentMethods'
import { useCohortsStore } from '@/stores/cohorts'
import { useScalesStore } from '@/stores/scales'
import { useCourseExportStore } from '@/stores/courseExport'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const courses = useCoursesStore()
const enrollmentStore = useEnrollmentStore()
const quizzesStore = useQuizzesStore()
const forumsStore = useForumsStore()
const choicesStore = useChoicesStore()
const glossariesStore = useGlossariesStore()
const wikisStore = useWikisStore()
const lessonsStore = useLessonsStore()
const workshopsStore = useWorkshopsStore()
const liveSessionsStore = useLiveSessionsStore()
const interactiveVideosStore = useInteractiveVideosStore()
const enrollmentMethodsStore = useEnrollmentMethodsStore()
const cohortsStore = useCohortsStore()
const scalesStore = useScalesStore()
const courseExportStore = useCourseExportStore()

const course = computed(() => courses.currentCourse)
const categories = ref([])
const categoryName = computed(() => categories.value.find(c => c.id === course.value?.category_id)?.name || null)
const enrollments = ref([])
const enrollEmail = ref('')
const enrollMessage = ref('')
const enrollmentSettings = ref(null)
const cohortSyncs = ref([])
const allCohorts = ref([])
const selectedCohortId = ref('')

const newSectionTitle = ref('')
const newResourceTitle = reactive({})
const newResourceContent = reactive({})
const newAssignmentTitle = reactive({})
const newAssignmentPoints = reactive({})
const newAssignmentScaleId = reactive({})
const newAssignmentGroupMode = reactive({})
const courseScales = ref([])
const newQuizTitle = reactive({})
const newQuizTimeLimit = reactive({})
const newForumTitle = reactive({})
const newForumGroupMode = reactive({})
const newChoiceTitle = reactive({})
const newChoiceOptionsRaw = reactive({})
const newChoiceAllowMultiple = reactive({})
const newChoiceGroupMode = reactive({})
const newGlossaryTitle = reactive({})
const newGlossaryAllowStudentEntries = reactive({})
const newGlossaryRequireApproval = reactive({})
const newWikiTitle = reactive({})
const newWikiMode = reactive({})
const newLessonTitle = reactive({})
const newWorkshopTitle = reactive({})
const newWorkshopStrategy = reactive({})
const newLiveSessionTitle = reactive({})
const newLiveSessionStart = reactive({})
const newLiveSessionEnd = reactive({})
const newVideoTitle = reactive({})
const newVideoSourceType = reactive({})
const newVideoUrl = reactive({})
const newVideoFile = reactive({})

const formatSettings = reactive({ format: 'topics', course_display: 'single_page', social_forum_id: '' })
const pageIndex = ref(0)
const exportWithStudentData = ref(false)

const displayedSections = computed(() => {
  if (!course.value) return []
  if (course.value.course_display === 'paginated') {
    return course.value.sections[pageIndex.value] ? [course.value.sections[pageIndex.value]] : []
  }
  return course.value.sections
})

const allForums = computed(() => {
  if (!course.value) return []
  return course.value.sections.flatMap((s) => s.forums || [])
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}

async function loadAll() {
  await courses.fetchCourse(route.params.id)
  categories.value = await courses.fetchCategories()
  enrollments.value = await enrollmentStore.fetchEnrollments(route.params.id)
  enrollmentSettings.value = await enrollmentMethodsStore.fetchSettings(route.params.id)
  cohortSyncs.value = await enrollmentMethodsStore.fetchCohortSyncs(route.params.id)
  allCohorts.value = await cohortsStore.fetchCohorts()
  courseScales.value = await scalesStore.fetchScales(route.params.id)
  formatSettings.format = course.value.format
  formatSettings.course_display = course.value.course_display
  formatSettings.social_forum_id = course.value.social_forum?.id || ''
}

async function onSaveFormat() {
  await courses.updateCourse(route.params.id, {
    format: formatSettings.format, course_display: formatSettings.course_display,
    social_forum_id: formatSettings.social_forum_id || null,
  })
  pageIndex.value = 0
  await loadAll()
}

async function onSaveEnrollmentSettings() {
  enrollmentSettings.value = await enrollmentMethodsStore.updateSettings(route.params.id, {
    self_enrollment_enabled: enrollmentSettings.value.self_enrollment_enabled,
    self_enrollment_key: enrollmentSettings.value.self_enrollment_key || null,
    guest_access_enabled: enrollmentSettings.value.guest_access_enabled,
    guest_access_key: enrollmentSettings.value.guest_access_key || null,
  })
}

async function onAddCohortSync() {
  if (!selectedCohortId.value) return
  await enrollmentMethodsStore.createCohortSync(route.params.id, selectedCohortId.value)
  selectedCohortId.value = ''
  cohortSyncs.value = await enrollmentMethodsStore.fetchCohortSyncs(route.params.id)
  enrollments.value = await enrollmentStore.fetchEnrollments(route.params.id)
}

async function onRemoveCohortSync(id) {
  await enrollmentMethodsStore.deleteCohortSync(id)
  cohortSyncs.value = await enrollmentMethodsStore.fetchCohortSyncs(route.params.id)
  enrollments.value = await enrollmentStore.fetchEnrollments(route.params.id)
}

async function onEnroll() {
  enrollMessage.value = ''
  try {
    const { data: user } = await axios.get('/users/lookup', { params: { email: enrollEmail.value } })
    await enrollmentStore.enrollUser(route.params.id, user.id, 'student')
    enrollEmail.value = ''
    enrollments.value = await enrollmentStore.fetchEnrollments(route.params.id)
  } catch (e) {
    enrollMessage.value = e.response?.data?.detail || t('teacher.courseDetail.enrollError')
  }
}

async function onUnenroll(id) {
  await enrollmentStore.unenroll(id)
  enrollments.value = await enrollmentStore.fetchEnrollments(route.params.id)
}

async function onAddSection() {
  await courses.createSection(route.params.id, { title: newSectionTitle.value, sort_order: (course.value.sections?.length || 0) + 1 })
  newSectionTitle.value = ''
  await loadAll()
}

async function onAddResource(sectionId) {
  const formData = new FormData()
  formData.append('resource_type', 'page')
  formData.append('title', newResourceTitle[sectionId] || 'Page')
  formData.append('page_content', newResourceContent[sectionId] || '')
  formData.append('sort_order', 0)
  await courses.createResource(sectionId, formData)
  newResourceTitle[sectionId] = ''
  newResourceContent[sectionId] = ''
  await loadAll()
}

async function onAddAssignment(sectionId) {
  await courses.createAssignment(sectionId, {
    title: newAssignmentTitle[sectionId] || 'Devoir',
    max_points: Number(newAssignmentPoints[sectionId]) || 100,
    scale_id: newAssignmentScaleId[sectionId] || null,
    submission_type: 'both',
    group_mode: !!newAssignmentGroupMode[sectionId],
  })
  newAssignmentTitle[sectionId] = ''
  newAssignmentPoints[sectionId] = ''
  newAssignmentScaleId[sectionId] = ''
  newAssignmentGroupMode[sectionId] = false
  await loadAll()
}

async function onAddQuiz(sectionId) {
  await quizzesStore.createQuiz(sectionId, {
    title: newQuizTitle[sectionId] || 'Quiz',
    time_limit_minutes: newQuizTimeLimit[sectionId] ? Number(newQuizTimeLimit[sectionId]) : null,
  })
  newQuizTitle[sectionId] = ''
  newQuizTimeLimit[sectionId] = ''
  await loadAll()
}

async function onAddForum(sectionId) {
  await forumsStore.createForum(sectionId, {
    title: newForumTitle[sectionId] || 'Forum',
    group_mode: newForumGroupMode[sectionId] || 'no_groups',
  })
  newForumTitle[sectionId] = ''
  newForumGroupMode[sectionId] = 'no_groups'
  await loadAll()
}

async function onAddChoice(sectionId) {
  const options = (newChoiceOptionsRaw[sectionId] || '').split(',').map((s) => s.trim()).filter(Boolean)
  if (!options.length) return
  await choicesStore.createChoice(sectionId, {
    title: newChoiceTitle[sectionId] || 'Sondage',
    allow_multiple: !!newChoiceAllowMultiple[sectionId],
    results_display: 'always',
    group_mode: newChoiceGroupMode[sectionId] || 'no_groups',
    options: options.map((option_text, sort_order) => ({ option_text, sort_order })),
  })
  newChoiceTitle[sectionId] = ''
  newChoiceGroupMode[sectionId] = 'no_groups'
  newChoiceOptionsRaw[sectionId] = ''
  newChoiceAllowMultiple[sectionId] = false
  await loadAll()
}

async function onAddGlossary(sectionId) {
  await glossariesStore.createGlossary(sectionId, {
    title: newGlossaryTitle[sectionId] || 'Glossaire',
    allow_student_entries: !!newGlossaryAllowStudentEntries[sectionId],
    require_approval: !!newGlossaryRequireApproval[sectionId],
  })
  newGlossaryTitle[sectionId] = ''
  newGlossaryAllowStudentEntries[sectionId] = false
  newGlossaryRequireApproval[sectionId] = false
  await loadAll()
}

async function onAddWiki(sectionId) {
  await wikisStore.createWiki(sectionId, {
    title: newWikiTitle[sectionId] || 'Wiki',
    mode: newWikiMode[sectionId] || 'collaborative',
  })
  newWikiTitle[sectionId] = ''
  newWikiMode[sectionId] = 'collaborative'
  await loadAll()
}

async function onAddLesson(sectionId) {
  await lessonsStore.createLesson(sectionId, { title: newLessonTitle[sectionId] || 'Leçon' })
  newLessonTitle[sectionId] = ''
  await loadAll()
}

async function onAddWorkshop(sectionId) {
  await workshopsStore.createWorkshop(sectionId, {
    title: newWorkshopTitle[sectionId] || 'Atelier', strategy: newWorkshopStrategy[sectionId] || 'accumulative',
  })
  newWorkshopTitle[sectionId] = ''
  newWorkshopStrategy[sectionId] = 'accumulative'
  await loadAll()
}

async function onAddLiveSession(sectionId) {
  await liveSessionsStore.createLiveSession(sectionId, {
    title: newLiveSessionTitle[sectionId] || 'Cours en direct',
    scheduled_start: newLiveSessionStart[sectionId] || null,
    scheduled_end: newLiveSessionEnd[sectionId] || null,
  })
  newLiveSessionTitle[sectionId] = ''
  newLiveSessionStart[sectionId] = ''
  newLiveSessionEnd[sectionId] = ''
  await loadAll()
}

function onVideoFileChange(event, sectionId) {
  newVideoFile[sectionId] = event.target.files[0] || null
}

async function onAddVideo(sectionId) {
  const sourceType = newVideoSourceType[sectionId] || 'url'
  if (!newVideoTitle[sectionId]) return
  const formData = new FormData()
  formData.append('title', newVideoTitle[sectionId])
  formData.append('source_type', sourceType)
  if (sourceType === 'url') {
    if (!newVideoUrl[sectionId]) return
    formData.append('video_url', newVideoUrl[sectionId])
  } else {
    if (!newVideoFile[sectionId]) return
    formData.append('file', newVideoFile[sectionId])
  }
  await interactiveVideosStore.createVideo(sectionId, formData)
  newVideoTitle[sectionId] = ''
  newVideoUrl[sectionId] = ''
  newVideoFile[sectionId] = null
  await loadAll()
}

async function onExport() {
  await courseExportStore.exportCourse(course.value.id, `${course.value.short_name}.json`, exportWithStudentData.value)
}

onMounted(loadAll)
</script>
