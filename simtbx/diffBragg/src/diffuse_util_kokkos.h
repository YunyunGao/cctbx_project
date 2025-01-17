#ifndef SIMTBX_DIFFBRAGG_DIFFUSE_UTIL_KOKKOS
#define SIMTBX_DIFFBRAGG_DIFFUSE_UTIL_KOKKOS

#include <simtbx/diffBragg/src/util_kokkos.h>

KOKKOS_FUNCTION
int gen_laue_mats(int laue_group_num, KOKKOS_MAT3 *lmats, KOKKOS_MAT3 rpa) {

  if (laue_group_num < 1 || laue_group_num >14 ){
    printf("Laue group number not in range 1-14; exiting\n");
    exit(1);
  }
  int num_mats;

  const double one_over_root2 = 1./sqrt(2.);

  if ( laue_group_num == 1 ) {
  // P -1

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

    num_mats= 1;
  }
  if ( laue_group_num == 2 ) {
  // P 1 1 2/m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -x,-y,z
    lmats[1] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

    num_mats= 2;
  }
  if ( laue_group_num == 3 ) {
  // P 1 2/m 1

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -x,y,-z
    lmats[1] << -1, 0, 0,
                 0, 1, 0,
                 0, 0,-1;

    num_mats= 2;
  }
  if ( laue_group_num == 4 ) {
  // P 2/m 1 1

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // x,-y,-z
    lmats[1] <<  1, 0, 0,
                 0,-1, 0,
                 0, 0,-1;

    num_mats= 2;
  }
  if ( laue_group_num == 5 ) {
  // P m m m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // x,-y,-z
    lmats[1] <<  1, 0, 0,
                 0,-1, 0,
                 0, 0,-1;

              // -x,y,-z
    lmats[2] << -1, 0, 0,
                 0, 1, 0,
                 0, 0,-1;

              // -x,-y,z
    lmats[3] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

    num_mats= 4;
  }
  if ( laue_group_num == 6 ) {
  // P 4/m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -y,x,z
    lmats[1] <<  0,-1, 0,
                 1, 0, 0,
                 0, 0, 1;

              // y,-x,z
    lmats[2] <<  0, 1, 0,
                -1, 0, 0,
                 0, 0, 1;

              // -x,-y,z
    lmats[3] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

    num_mats= 4;
  }
  if ( laue_group_num == 7 ) {
  // P 4/m m m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -y,x,z
    lmats[1] <<  0,-1, 0,
                 1, 0, 0,
                 0, 0, 1;

              // y,-x,z
    lmats[2] <<  0, 1, 0,
                -1, 0, 0,
                 0, 0, 1;

              // x,-y,-z
    lmats[3] <<  1, 0, 0,
                 0,-1, 0,
                 0, 0,-1;

              // -x,y,-z
    lmats[4] << -1, 0, 0,
                 0, 1, 0,
                 0, 0,-1;

              // -x,-y,z
    lmats[5] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

              // y,x,-z
    lmats[6] <<  0, 1, 0,
                 1, 0, 0,
                 0, 0,-1;

              // -y,-x,-z
    lmats[7] <<  0,-1, 0,
                -1, 0, 0,
                 0, 0,-1;

    num_mats= 8;
  }
  if ( laue_group_num == 8 ) {
  // P -3

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -y,x-y,z
    lmats[1] <<  0,-1, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0, 1;

              // -x+y,-x,z
    lmats[2] << -one_over_root2, one_over_root2, 0,
                -1, 0, 0,
                 0, 0, 1;

    num_mats= 3;
  }
  if ( laue_group_num == 9 ) {
  // P -3 m 1

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -y,x-y,z
    lmats[1] <<  0,-1, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0, 1;

              // -x+y,-x,z
    lmats[2] << -one_over_root2, one_over_root2, 0,
                -1, 0, 0,
                 0, 0, 1;

              // x-y,-y,-z
    lmats[3] <<  one_over_root2,-one_over_root2, 0,
                 0,-1, 0,
                 0, 0,-1;

              // -x,-x+y,-z
    lmats[4] << -1, 0, 0,
                -one_over_root2, one_over_root2, 0,
                 0, 0,-1;

              // y,x,-z
    lmats[5] <<  0, 1, 0,
                 1, 0, 0,
                 0, 0,-1;

    num_mats= 6;
  }
  if ( laue_group_num == 10 ) {
  // P -3 1 m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // -y,x-y,z
    lmats[1] <<  0,-1, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0, 1;

              // -x+y,-x,z
    lmats[2] << -one_over_root2, one_over_root2, 0,
                -1, 0, 0,
                 0, 0, 1;

              // -y,-x,-z
    lmats[3] <<  0,-1, 0,
                -1, 0, 0,
                 0, 0,-1;

              // -x+y,y,-z
    lmats[4] << -one_over_root2, one_over_root2, 0,
                 0, 1, 0,
                 0, 0,-1;

              // x,x-y,-z
    lmats[5] <<  1, 0, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0,-1;

    num_mats= 6;
  }
  if ( laue_group_num == 11 ) {
  // P 6/m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // x-y,x,z
    lmats[1] <<  one_over_root2,-one_over_root2, 0,
                 1, 0, 0,
                 0, 0, 1;

              // y,-x+y,z
    lmats[2] <<  0, 1, 0,
                -one_over_root2, one_over_root2, 0,
                 0, 0, 1;

              // -y,x-y,z
    lmats[3] <<  0,-1, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0, 1;

              // -x+y,-x,z
    lmats[4] << -one_over_root2, one_over_root2, 0,
                -1, 0, 0,
                 0, 0, 1;

              // -x,-y,z
    lmats[5] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

    num_mats= 6;
  }
  if ( laue_group_num == 12 ) {
  // P 6/m m m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // x-y,x,z
    lmats[1] <<  one_over_root2,-one_over_root2, 0,
                 1, 0, 0,
                 0, 0, 1;

              // y,-x+y,z
    lmats[2] <<  0, 1, 0,
                -one_over_root2, one_over_root2, 0,
                 0, 0, 1;

              // -y,x-y,z
    lmats[3] <<  0,-1, 0,
                 one_over_root2,-one_over_root2, 0,
                 0, 0, 1;

              // -x+y,-x,z
    lmats[4] << -one_over_root2, one_over_root2, 0,
                -1, 0, 0,
                 0, 0, 1;

              // x-y,-y,-z
    lmats[5] <<  one_over_root2,-one_over_root2, 0,
                 0,-1, 0,
                 0, 0,-1;

              // -x,-x+y,-z
    lmats[6] << -1, 0, 0,
                -one_over_root2, one_over_root2, 0,
                 0, 0,-1;

              // -x,-y,z
    lmats[7] << -1, 0, 0,
                 0,-1, 0,
                 0, 0, 1;

              // y,x,-z
    lmats[8] <<  0, 1, 0,
                 1, 0, 0,
                 0, 0,-1;

              // -y,-x,-z
    lmats[9] <<  0,-1, 0,
                -1, 0, 0,
                 0, 0,-1;

              // -x+y,y,-z
    lmats[10] << -one_over_root2, one_over_root2, 0,
                  0, 1, 0,
                  0, 0,-1;

              // x,x-y,-z
    lmats[11] <<  1, 0, 0,
                  one_over_root2,-one_over_root2, 0,
                  0, 0,-1;

    num_mats= 12;
  }
  if ( laue_group_num == 13 ) {
  // P m -3

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // z,x,y
    lmats[1] <<  0, 0, 1,
                 1, 0, 0,
                 0, 1, 0;

              // y,z,x
    lmats[2] <<  0, 1, 0,
                 0, 0, 1,
                 1, 0, 0;

              // -y,-z,x
    lmats[3] <<  0,-1, 0,
                 0, 0,-1,
                 1, 0, 0;

              // z,-x,-y
    lmats[4] <<  0, 0, 1,
                -1, 0, 0,
                 0,-1, 0;

              // -y,z,-x
    lmats[5] <<  0,-1, 0,
                 0, 0, 1,
                -1, 0, 0;

              // -z,-x,y
    lmats[6] <<  0, 0,-1,
                -1, 0, 0,
                 0, 1, 0;

              // -z,x,-y
    lmats[7] <<  0, 0,-1,
                 1, 0, 0,
                 0,-1, 0;

              // y,-z,-x
    lmats[8] <<  0, 1, 0,
                 0, 0,-1,
                -1, 0, 0;

              // x,-y,-z
    lmats[9] <<  1, 0, 0,
                 0,-1, 0,
                 0, 0,-1;

              // -x,y,-z
    lmats[10] << -1, 0, 0,
                  0, 1, 0,
                  0, 0,-1;

              // -x,-y,z
    lmats[11] << -1, 0, 0,
                  0,-1, 0,
                  0, 0, 1;

    num_mats= 12;
  }
  if ( laue_group_num == 14 ) {
  // P m -3 m

              // x,y,z
    lmats[0] <<  1, 0, 0,
                 0, 1, 0,
                 0, 0, 1;

              // x,-z,y
    lmats[1] <<  1, 0, 0,
                 0, 0,-1,
                 0, 1, 0;

              // x,z,-y
    lmats[2] <<  1, 0, 0,
                 0, 0, 1,
                 0,-1, 0;

              // z,y,-x
    lmats[3] <<  0, 0, 1,
                 0, 1, 0,
                -1, 0, 0;

              // -z,y,x
    lmats[4] <<  0, 0,-1,
                 0, 1, 0,
                 1, 0, 0;

              // -y,x,z
    lmats[5] <<  0,-1, 0,
                 1, 0, 0,
                 0, 0, 1;

              // y,-x,z
    lmats[6] <<  0, 1, 0,
                -1, 0, 0,
                 0, 0, 1;

              // z,x,y
    lmats[7] <<  0, 0, 1,
                 1, 0, 0,
                 0, 1, 0;

              // y,z,x
    lmats[8] <<  0, 1, 0,
                 0, 0, 1,
                 1, 0, 0;

              // -y,-z,x
    lmats[9] <<  0,-1, 0,
                 0, 0,-1,
                 1, 0, 0;

              // z,-x,-y
    lmats[10] <<  0, 0, 1,
                 -1, 0, 0,
                  0,-1, 0;

              // -y,z,-x
    lmats[11] <<  0,-1, 0,
                  0, 0, 1,
                 -1, 0, 0;

              // -z,-x,y
    lmats[12] <<  0, 0,-1,
                 -1, 0, 0,
                  0, 1, 0;

              // -z,x,-y
    lmats[13] <<  0, 0,-1,
                  1, 0, 0,
                  0,-1, 0;

              // y,-z,-x
    lmats[14] <<  0, 1, 0,
                  0, 0,-1,
                 -1, 0, 0;

              // x,-y,-z
    lmats[15] <<  1, 0, 0,
                  0,-1, 0,
                  0, 0,-1;

              // -x,y,-z
    lmats[16] << -1, 0, 0,
                  0, 1, 0,
                  0, 0,-1;

              // -x,-y,z
    lmats[17] << -1, 0, 0,
                  0,-1, 0,
                  0, 0, 1;

              // y,x,-z
    lmats[18] <<  0, 1, 0,
                  1, 0, 0,
                  0, 0,-1;

              // -y,-x,-z
    lmats[19] <<  0,-1, 0,
                 -1, 0, 0,
                  0, 0,-1;

              // z,-y,x
    lmats[20] <<  0, 0, 1,
                  0,-1, 0,
                  1, 0, 0;

              // -z,-y,-x
    lmats[21] <<  0, 0,-1,
                  0,-1, 0,
                 -1, 0, 0;

              // -x,z,y
    lmats[22] << -1, 0, 0,
                  0, 0, 1,
                  0, 1, 0;

              // -x,-z,-y
    lmats[23] << -1, 0, 0,
                  0, 0,-1,
                  0,-1, 0;

    num_mats = 24;
  }

  for (int i_mat=0; i_mat < num_mats; i_mat ++){
    lmats[i_mat] = lmats[i_mat] * rpa;
  }
  return num_mats;
};

KOKKOS_FUNCTION
void calc_diffuse_at_hkl(KOKKOS_VEC3 H_vec, KOKKOS_VEC3 H0, KOKKOS_VEC3 dHH, KOKKOS_VEC3 Hmin, KOKKOS_VEC3 Hmax, KOKKOS_VEC3 Hrange, KOKKOS_MAT3 Ainv, const vector_cudareal_t FhklLinear, int num_laue_mats, const KOKKOS_MAT3 *laue_mats, KOKKOS_MAT3 anisoG_local, KOKKOS_MAT3 anisoU_local, const KOKKOS_MAT3 *dG_dgam, bool refine_diffuse, CUDAREAL *I0, CUDAREAL *step_diffuse_param){
  CUDAREAL four_mpi_sq = 4.*M_PI*M_PI;
  // loop over laue matrices
  int num_stencil_points = (2*dHH[0] + 1) * (2*dHH[1] + 1) * (2*dHH[2] + 1);
  bool h_bounded= (H0[0]+dHH[0]<=Hmax[0]) && (H0[0]-dHH[0]>=Hmin[0]) ;
  bool k_bounded= (H0[1]+dHH[1]<=Hmax[1]) && (H0[1]-dHH[1]>=Hmin[1]) ;
  bool l_bounded= (H0[2]+dHH[2]<=Hmax[2]) && (H0[2]-dHH[2]>=Hmin[2]) ;
  if (h_bounded && k_bounded && l_bounded) {
    int Fhkl_linear_index_0 = (H0[0]-Hmin[0]) * Hrange[1] * Hrange[2]
      + (H0[1]-Hmin[1]) * Hrange[2] + (H0[2]-Hmin[2]);
    CUDAREAL _F_cell_0 = FhklLinear(Fhkl_linear_index_0);
    KOKKOS_MAT3 Ginv = anisoG_local.inverse();
    CUDAREAL anisoG_determ = anisoG_local.determinant();
    for (int hh=-dHH[0]; hh <= dHH[0]; hh++){
      for (int kk=-dHH[1]; kk <= dHH[1]; kk++){
        for (int ll=-dHH[2]; ll <= dHH[2]; ll++){
          CUDAREAL ID_this = 0;
          CUDAREAL step_diffuse_param_this[6]  = {0,0,0,0,0,0};
          int Fhkl_linear_index_this = (H0[0]+hh-Hmin[0]) * Hrange[1] * Hrange[2]
            + (H0[1]+kk-Hmin[1]) * Hrange[2] + (H0[2]+ll-Hmin[2]);
          CUDAREAL _F_cell_this = FhklLinear(Fhkl_linear_index_this);
          CUDAREAL _this_diffuse_scale;
          if (_F_cell_0 != 0.0)
            _this_diffuse_scale = _F_cell_this/_F_cell_0;
          else
            _this_diffuse_scale = 1.0;

          _this_diffuse_scale *= _this_diffuse_scale/(CUDAREAL)num_laue_mats/
            (CUDAREAL)num_stencil_points;
          // Use (a-b, a+b, c) as the principal axes of the diffuse model
          // TODO: Add an option to select (a, b, c) as the principal axes

          for ( int iL = 0; iL < num_laue_mats; iL++ ){
            KOKKOS_VEC3 Q0 =Ainv*laue_mats[iL]*H0;
            CUDAREAL exparg = four_mpi_sq*Q0.dot(anisoU_local*Q0);
            CUDAREAL dwf = exp(-exparg);
            KOKKOS_VEC3 H0_offset(H0[0]+hh, H0[1]+kk, H0[2]+ll);
            KOKKOS_VEC3 delta_H_offset = H_vec - H0_offset;
            KOKKOS_VEC3 delta_Q = Ainv*laue_mats[iL]*delta_H_offset;
            KOKKOS_VEC3 anisoG_q = anisoG_local*delta_Q;

            CUDAREAL V_dot_V = anisoG_q.dot(anisoG_q);
            CUDAREAL gamma_portion_denom = (1.+ V_dot_V* four_mpi_sq);
            gamma_portion_denom *= gamma_portion_denom;
            CUDAREAL gamma_portion = 8.*M_PI*anisoG_determ /
              gamma_portion_denom;
            CUDAREAL this_I_latt_diffuse = dwf*exparg*gamma_portion;

            ID_this += this_I_latt_diffuse;
            if (refine_diffuse){ // add the contributions to diffuse scattering gradients here
              for (int i_gam=0; i_gam<3; i_gam++){
                KOKKOS_VEC3 dV = dG_dgam[i_gam]*delta_Q;
                CUDAREAL V_dot_dV = anisoG_q.dot(dV);
                CUDAREAL deriv = (Ginv*dG_dgam[i_gam]).trace() - 4.*four_mpi_sq*V_dot_dV/(1+four_mpi_sq*V_dot_V);
                step_diffuse_param_this[i_gam] += gamma_portion*deriv*dwf*exparg;
              }
              KOKKOS_MAT3 dU_dsigma;
              // dU_dsigma << 0,0,0,0,0,0,0,0,0;
              for (int i_sig = 0;i_sig<3; i_sig++){
                dU_dsigma(i_sig, i_sig) = 2.*sqrt(anisoU_local(i_sig,i_sig));
                CUDAREAL dexparg = four_mpi_sq*Q0.dot(dU_dsigma*Q0);
                dU_dsigma(i_sig, i_sig) = 0.;
                step_diffuse_param_this[i_sig+3] += gamma_portion*dwf*dexparg*(1. - exparg);
              }
            }
          } // end loop over iL (laue group mats)
          // Update the lattice interference term here to include diffuse scattering (F_latt squared)
          *I0 += ID_this * _this_diffuse_scale;

          for (int idp=0; idp < 6; idp++)
            step_diffuse_param[idp] += step_diffuse_param_this[idp]*_this_diffuse_scale;
        } // end ll loop
      } // end kk loop
    } // end hh loop
  } // end if bounded
}

#endif
